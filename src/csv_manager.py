"""
CSV 파일 관리 모듈

이 모듈은 블로그 URL의 인덱싱 상태를 CSV 파일로 관리하는 기능을 제공합니다.
각 URL의 상태(PENDING/SUCCESS/FAILED)와 날짜 정보를 추적합니다.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


# CSV 파일 필드명 정의
CSV_HEADERS = ['url', 'status', 'lastmod', 'created_at', 'updated_at', 'retry_count']

# 상태 값 정의
STATUS_PENDING = 'PENDING'  # 인덱싱 대기 중
STATUS_SUCCESS = 'SUCCESS'  # 인덱싱 성공
STATUS_FAILED = 'FAILED'    # 인덱싱 실패 (3회 재시도 후)


def ensure_data_directory(csv_path: str) -> None:
    """
    CSV 파일이 저장될 디렉토리가 존재하는지 확인하고,
    없으면 생성합니다.

    Args:
        csv_path: CSV 파일 경로

    Note:
        예: csv_path가 'data/urls.csv'이면 'data' 폴더를 생성합니다.
    """
    directory = os.path.dirname(csv_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"📁 디렉토리 생성: {directory}")


def read_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    CSV 파일을 읽어서 URL 정보 리스트로 반환합니다.

    Args:
        csv_path: CSV 파일 경로

    Returns:
        URL 정보 딕셔너리 리스트
        [{'url': 'URL', 'status': '상태', 'lastmod': '날짜', ...}, ...]

    Note:
        - 파일이 없는 경우 빈 리스트를 반환합니다
        - CSV 인코딩은 UTF-8을 사용합니다
    """
    # 파일이 존재하지 않으면 빈 리스트 반환
    if not os.path.exists(csv_path):
        print(f"ℹ️  CSV 파일 없음: {csv_path}")
        return []

    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            # DictReader를 사용하여 각 행을 딕셔너리로 읽기
            reader = csv.DictReader(f)
            data = list(reader)
            print(f"📖 CSV 파일 읽기 완료: {len(data)}개 항목")
            return data

    except Exception as e:
        print(f"❌ CSV 파일 읽기 실패: {csv_path}")
        print(f"   에러: {str(e)}")
        return []


def write_csv(csv_path: str, data: List[Dict[str, str]]) -> bool:
    """
    URL 정보 리스트를 CSV 파일로 저장합니다.

    Args:
        csv_path: CSV 파일 경로
        data: URL 정보 딕셔너리 리스트

    Returns:
        True: 저장 성공
        False: 저장 실패

    Note:
        - 기존 파일이 있으면 덮어씁니다
        - 헤더(url, status, lastmod, ...)는 자동으로 추가됩니다
    """
    try:
        # 디렉토리 생성 확인
        ensure_data_directory(csv_path)

        # CSV 파일 쓰기
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)

            # 헤더 작성
            writer.writeheader()

            # 데이터 작성
            writer.writerows(data)

        print(f"💾 CSV 파일 저장 완료: {len(data)}개 항목")
        return True

    except Exception as e:
        print(f"❌ CSV 파일 저장 실패: {csv_path}")
        print(f"   에러: {str(e)}")
        return False


def get_url_status(csv_path: str, url: str) -> Optional[str]:
    """
    특정 URL의 현재 상태를 확인합니다.

    Args:
        csv_path: CSV 파일 경로
        url: 확인할 URL

    Returns:
        상태 값 (PENDING/SUCCESS/FAILED) 또는 None (URL이 없는 경우)

    Example:
        status = get_url_status('data/urls.csv', 'https://blog.tistory.com/123')
        if status == 'PENDING':
            print("인덱싱 대기 중")
    """
    data = read_csv(csv_path)

    # URL이 일치하는 항목 찾기
    for row in data:
        if row['url'] == url:
            return row.get('status')

    # URL을 찾지 못한 경우
    return None


def add_url(csv_path: str, url: str, lastmod: str = '') -> bool:
    """
    새로운 URL을 CSV에 추가합니다.
    이미 존재하는 URL인 경우 추가하지 않습니다.

    Args:
        csv_path: CSV 파일 경로
        url: 추가할 URL
        lastmod: 마지막 수정일 (선택)

    Returns:
        True: 추가 성공
        False: 이미 존재하거나 추가 실패

    Note:
        - 새로 추가된 URL의 초기 상태는 PENDING입니다
        - created_at과 updated_at은 현재 시간으로 자동 설정됩니다
        - retry_count는 0으로 초기화됩니다
    """
    data = read_csv(csv_path)

    # 이미 존재하는 URL인지 확인
    for row in data:
        if row['url'] == url:
            print(f"ℹ️  이미 존재하는 URL: {url}")
            return False

    # 현재 시간 (ISO 8601 형식)
    now = datetime.now().isoformat()

    # 새 URL 정보 추가
    new_row = {
        'url': url,
        'status': STATUS_PENDING,      # 초기 상태는 PENDING
        'lastmod': lastmod,
        'created_at': now,
        'updated_at': now,
        'retry_count': '0'             # 재시도 횟수 0으로 초기화
    }

    data.append(new_row)

    # CSV 파일 저장
    return write_csv(csv_path, data)


def update_url_status(csv_path: str, url: str, status: str, increment_retry: bool = False) -> bool:
    """
    특정 URL의 상태를 업데이트합니다.

    Args:
        csv_path: CSV 파일 경로
        url: 업데이트할 URL
        status: 새로운 상태 (PENDING/SUCCESS/FAILED)
        increment_retry: True이면 재시도 횟수를 1 증가시킴

    Returns:
        True: 업데이트 성공
        False: URL을 찾지 못했거나 업데이트 실패

    Note:
        - updated_at은 현재 시간으로 자동 업데이트됩니다
        - increment_retry=True인 경우 retry_count가 증가합니다
    """
    data = read_csv(csv_path)

    # URL이 일치하는 항목 찾아서 업데이트
    updated = False
    for row in data:
        if row['url'] == url:
            # 상태 업데이트
            row['status'] = status
            row['updated_at'] = datetime.now().isoformat()

            # 재시도 횟수 증가 (옵션)
            if increment_retry:
                current_retry = int(row.get('retry_count', 0))
                row['retry_count'] = str(current_retry + 1)

            updated = True
            break

    if not updated:
        print(f"❌ URL을 찾을 수 없음: {url}")
        return False

    # CSV 파일 저장
    return write_csv(csv_path, data)


def get_pending_urls(csv_path: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """
    PENDING 상태인 URL 목록을 반환합니다.

    Args:
        csv_path: CSV 파일 경로
        limit: 최대 반환 개수 (None이면 전체)

    Returns:
        PENDING 상태 URL 정보 딕셔너리 리스트

    Note:
        - Google Indexing API는 일일 200개 제한이 있으므로
          limit=200으로 설정하여 사용하는 것을 권장합니다
    """
    data = read_csv(csv_path)

    # PENDING 상태인 항목만 필터링
    pending = [row for row in data if row.get('status') == STATUS_PENDING]

    # limit이 지정된 경우 해당 개수만 반환
    if limit is not None:
        pending = pending[:limit]

    print(f"📋 PENDING 상태 URL: {len(pending)}개")
    return pending


def add_urls_batch(csv_path: str, urls: List[Dict[str, str]]) -> int:
    """
    여러 URL을 한 번에 CSV에 추가합니다.
    사이트맵에서 추출한 URL 목록을 초기화할 때 사용합니다.

    Args:
        csv_path: CSV 파일 경로
        urls: URL 정보 딕셔너리 리스트
              [{'loc': 'URL', 'lastmod': '날짜'}, ...]

    Returns:
        추가된 URL 개수

    Note:
        - 이미 존재하는 URL은 건너뜁니다
        - 새로 추가된 URL의 초기 상태는 PENDING입니다
    """
    data = read_csv(csv_path)

    # 기존 URL 목록 (중복 체크용)
    existing_urls = {row['url'] for row in data}

    # 현재 시간
    now = datetime.now().isoformat()

    # 추가된 개수 카운터
    added_count = 0

    # 각 URL 처리
    for url_info in urls:
        url = url_info.get('loc', '')
        lastmod = url_info.get('lastmod', '')

        # 빈 URL이거나 이미 존재하는 경우 건너뛰기
        if not url or url in existing_urls:
            continue

        # 새 URL 정보 추가
        new_row = {
            'url': url,
            'status': STATUS_PENDING,
            'lastmod': lastmod,
            'created_at': now,
            'updated_at': now,
            'retry_count': '0'
        }

        data.append(new_row)
        existing_urls.add(url)  # 중복 체크 세트에 추가
        added_count += 1

    # CSV 파일 저장
    if added_count > 0:
        write_csv(csv_path, data)
        print(f"✅ {added_count}개 URL 추가 완료")
    else:
        print(f"ℹ️  새로 추가할 URL 없음 (모두 기존 URL)")

    return added_count


def get_statistics(csv_path: str) -> Dict[str, int]:
    """
    CSV 파일의 통계 정보를 반환합니다.

    Args:
        csv_path: CSV 파일 경로

    Returns:
        통계 정보 딕셔너리
        {
            'total': 전체 URL 개수,
            'pending': PENDING 개수,
            'success': SUCCESS 개수,
            'failed': FAILED 개수
        }

    Example:
        stats = get_statistics('data/urls.csv')
        print(f"전체: {stats['total']}, 성공: {stats['success']}")
    """
    data = read_csv(csv_path)

    # 상태별 개수 계산
    stats = {
        'total': len(data),
        'pending': 0,
        'success': 0,
        'failed': 0
    }

    for row in data:
        status = row.get('status', '')
        if status == STATUS_PENDING:
            stats['pending'] += 1
        elif status == STATUS_SUCCESS:
            stats['success'] += 1
        elif status == STATUS_FAILED:
            stats['failed'] += 1

    return stats
