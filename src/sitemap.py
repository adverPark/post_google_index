"""
사이트맵 다운로드 및 파싱 모듈

이 모듈은 티스토리 사이트맵 XML을 다운로드하고 파싱하여
블로그 게시글 URL 목록을 추출하는 기능을 제공합니다.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import requests
import re


def download_sitemap(url: str) -> Optional[str]:
    """
    사이트맵 XML을 다운로드합니다.

    Args:
        url: 사이트맵 URL (예: https://yourblog.tistory.com/sitemap.xml)

    Returns:
        XML 문자열 (성공 시) 또는 None (실패 시)

    Raises:
        requests.RequestException: HTTP 요청 실패 시
    """
    try:
        # User-Agent 헤더를 추가하여 봇 차단 방지
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 사이트맵 다운로드 (타임아웃 10초)
        response = requests.get(url, headers=headers, timeout=10)

        # HTTP 상태 코드 확인 (200이 아니면 예외 발생)
        response.raise_for_status()

        # UTF-8로 인코딩된 XML 텍스트 반환
        return response.text

    except requests.RequestException as e:
        print(f"❌ 사이트맵 다운로드 실패: {url}")
        print(f"   에러: {str(e)}")
        return None


def parse_sitemap_urls(xml_content: str) -> List[Dict[str, str]]:
    """
    사이트맵 XML에서 URL 정보를 추출합니다.

    Args:
        xml_content: 사이트맵 XML 문자열

    Returns:
        URL 정보 딕셔너리 리스트
        [{'loc': 'URL', 'lastmod': '수정일자'}, ...]

    Note:
        - XML 네임스페이스를 고려하여 파싱합니다
        - lastmod가 없는 경우 빈 문자열로 처리됩니다
    """
    try:
        # XML 파싱
        root = ET.fromstring(xml_content)

        # XML 네임스페이스 정의 (사이트맵 표준 네임스페이스)
        namespaces = {
            'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        }

        # URL 정보를 저장할 리스트
        urls = []

        # 모든 <url> 요소를 찾아서 처리
        for url_element in root.findall('ns:url', namespaces):
            # <loc> 태그에서 URL 추출 (필수)
            loc = url_element.find('ns:loc', namespaces)

            # <lastmod> 태그에서 수정일자 추출 (선택)
            lastmod = url_element.find('ns:lastmod', namespaces)

            # URL이 존재하는 경우만 리스트에 추가
            if loc is not None and loc.text:
                urls.append({
                    'loc': loc.text.strip(),
                    'lastmod': lastmod.text.strip() if lastmod is not None and lastmod.text else ''
                })

        return urls

    except ET.ParseError as e:
        print(f"❌ XML 파싱 실패: {str(e)}")
        return []


def parse_sitemap_index(xml_content: str) -> List[str]:
    """
    사이트맵 인덱스 파일에서 하위 사이트맵 URL 목록을 추출합니다.

    Args:
        xml_content: 사이트맵 인덱스 XML 문자열

    Returns:
        하위 사이트맵 URL 리스트

    Note:
        사이트맵 인덱스는 여러 개의 사이트맵을 포함하는 상위 파일입니다.
        예: sitemap.xml -> sitemap1.xml, sitemap2.xml, ...
    """
    try:
        # XML 파싱
        root = ET.fromstring(xml_content)

        # XML 네임스페이스 정의
        namespaces = {
            'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        }

        # 사이트맵 URL을 저장할 리스트
        sitemap_urls = []

        # 모든 <sitemap> 요소를 찾아서 처리
        for sitemap_element in root.findall('ns:sitemap', namespaces):
            # <loc> 태그에서 사이트맵 URL 추출
            loc = sitemap_element.find('ns:loc', namespaces)

            # URL이 존재하는 경우만 리스트에 추가
            if loc is not None and loc.text:
                sitemap_urls.append(loc.text.strip())

        return sitemap_urls

    except ET.ParseError as e:
        print(f"❌ 사이트맵 인덱스 파싱 실패: {str(e)}")
        return []


def is_sitemap_index(xml_content: str) -> bool:
    """
    XML이 사이트맵 인덱스인지 일반 사이트맵인지 판별합니다.

    Args:
        xml_content: XML 문자열

    Returns:
        True: 사이트맵 인덱스
        False: 일반 사이트맵

    Note:
        사이트맵 인덱스는 <sitemapindex> 루트 태그를 가집니다.
        일반 사이트맵은 <urlset> 루트 태그를 가집니다.
    """
    try:
        root = ET.fromstring(xml_content)
        # 루트 태그 이름에 'sitemapindex'가 포함되어 있는지 확인
        return 'sitemapindex' in root.tag.lower()
    except ET.ParseError:
        return False


def get_all_urls_from_sitemap(sitemap_url: str) -> List[Dict[str, str]]:
    """
    사이트맵에서 모든 URL을 추출합니다.
    사이트맵 인덱스인 경우 모든 하위 사이트맵을 순회합니다.

    Args:
        sitemap_url: 사이트맵 URL

    Returns:
        URL 정보 딕셔너리 리스트
        [{'loc': 'URL', 'lastmod': '수정일자'}, ...]

    Note:
        - 사이트맵 인덱스를 자동으로 감지하고 처리합니다
        - 모든 하위 사이트맵을 순회하여 URL을 수집합니다
    """
    # 사이트맵 다운로드
    xml_content = download_sitemap(sitemap_url)
    if not xml_content:
        return []

    # 사이트맵 인덱스인지 확인
    if is_sitemap_index(xml_content):
        print(f"📂 사이트맵 인덱스 파일 감지: {sitemap_url}")

        # 하위 사이트맵 URL 목록 추출
        sitemap_urls = parse_sitemap_index(xml_content)
        print(f"📋 하위 사이트맵 {len(sitemap_urls)}개 발견")

        # 모든 URL을 수집할 리스트
        all_urls = []

        # 각 하위 사이트맵에서 URL 추출
        for idx, sub_sitemap_url in enumerate(sitemap_urls, 1):
            print(f"🔄 [{idx}/{len(sitemap_urls)}] {sub_sitemap_url} 처리 중...")

            # 하위 사이트맵 다운로드
            sub_xml_content = download_sitemap(sub_sitemap_url)
            if sub_xml_content:
                # URL 추출 및 병합
                urls = parse_sitemap_urls(sub_xml_content)
                all_urls.extend(urls)
                print(f"   ✅ {len(urls)}개 URL 추출")

        return all_urls

    else:
        # 일반 사이트맵인 경우 바로 URL 추출
        print(f"📄 일반 사이트맵 파일: {sitemap_url}")
        urls = parse_sitemap_urls(xml_content)
        print(f"✅ {len(urls)}개 URL 추출")
        return urls


def sort_urls_by_date(urls: List[Dict[str, str]], descending: bool = True) -> List[Dict[str, str]]:
    """
    URL 목록을 날짜순으로 정렬합니다.

    Args:
        urls: URL 정보 딕셔너리 리스트
        descending: True면 최신순(내림차순), False면 오래된순(오름차순)

    Returns:
        날짜순으로 정렬된 URL 리스트

    Note:
        - lastmod 값이 없는 URL은 정렬 우선순위가 낮습니다
        - ISO 8601 형식의 날짜를 파싱합니다 (예: 2025-01-15T10:30:25+09:00)
    """
    def get_date_key(url_info: Dict[str, str]) -> datetime:
        """정렬 키를 생성하는 헬퍼 함수"""
        lastmod = url_info.get('lastmod', '')

        if not lastmod:
            # lastmod가 없는 경우 가장 오래된 날짜로 설정
            return datetime.min

        try:
            # ISO 8601 형식 날짜 파싱
            # 예: 2025-01-15T10:30:25+09:00
            # 타임존 정보를 제거하고 파싱 (간단한 처리)
            date_str = lastmod.split('+')[0].split('Z')[0]
            return datetime.fromisoformat(date_str)
        except (ValueError, AttributeError):
            # 파싱 실패 시 가장 오래된 날짜로 설정
            return datetime.min

    # 날짜순으로 정렬
    return sorted(urls, key=get_date_key, reverse=descending)


def filter_post_urls(urls: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    URL 목록에서 블로그 글 페이지만 필터링합니다.
    카테고리, 태그, 메인 페이지, 모바일 URL 등은 제외됩니다.

    Args:
        urls: URL 정보 딕셔너리 리스트

    Returns:
        블로그 글 페이지만 포함된 URL 리스트

    Note:
        티스토리 URL 패턴:
        - 글 페이지: https://blog.tistory.com/123 또는 https://blog.tistory.com/notice/123
        - 제외 대상: /category/, /tag/, /pages/, /m/ (모바일), 메인 페이지 등
    """
    post_urls = []

    for url_info in urls:
        url = url_info['loc']

        # 모바일 URL 제외 (/m/로 시작하는 경로)
        # 예: https://blog.tistory.com/m/123 (제외)
        if '/m/' in url:
            continue

        # 글 페이지 패턴: 도메인/숫자 또는 도메인/경로/숫자
        # 예: https://blog.tistory.com/123
        #     https://blog.tistory.com/notice/456
        if re.match(r'^https?://[^/]+/(\w+/)?(\d+)$', url):
            # 카테고리, 태그, 페이지 등은 제외
            if not any(excluded in url for excluded in ['/category', '/tag', '/page']):
                post_urls.append(url_info)

    return post_urls


def sort_urls_by_number(urls: List[Dict[str, str]], descending: bool = True) -> List[Dict[str, str]]:
    """
    URL 목록을 URL 번호순으로 정렬합니다.

    Args:
        urls: URL 정보 딕셔너리 리스트
        descending: True면 큰 번호부터(내림차순), False면 작은 번호부터(오름차순)

    Returns:
        URL 번호순으로 정렬된 URL 리스트

    Note:
        - URL에서 마지막 숫자를 추출하여 정렬합니다
        - 예: /407 > /406 > /405 (descending=True)
        - 숫자를 추출할 수 없는 URL은 우선순위가 낮습니다
    """
    def get_url_number(url_info: Dict[str, str]) -> int:
        """URL에서 번호를 추출하는 헬퍼 함수"""
        url = url_info.get('loc', '')

        # URL 마지막 부분에서 숫자 추출
        # 예: https://blog.tistory.com/123 -> 123
        #     https://blog.tistory.com/notice/456 -> 456
        match = re.search(r'/(\d+)$', url)
        if match:
            return int(match.group(1))

        # 숫자를 찾지 못한 경우 0 반환 (우선순위 낮음)
        return 0

    # URL 번호순으로 정렬
    return sorted(urls, key=get_url_number, reverse=descending)
