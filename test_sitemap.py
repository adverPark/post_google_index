"""
사이트맵 모듈 테스트 스크립트

이 스크립트는 src/sitemap.py 모듈의 기능을 테스트합니다.
실제 티스토리 사이트맵 URL을 사용하여 테스트할 수 있습니다.
"""

from src.sitemap import (
    download_sitemap,
    parse_sitemap_urls,
    parse_sitemap_index,
    is_sitemap_index,
    get_all_urls_from_sitemap,
    sort_urls_by_date,
    sort_urls_by_number,
    filter_post_urls
)


def test_with_example_sitemap():
    """
    예시 사이트맵으로 테스트합니다.

    실제 티스토리 사이트맵 URL이 있다면 아래 URL을 변경하여 테스트하세요.
    """
    print("=" * 60)
    print("🧪 사이트맵 모듈 테스트")
    print("=" * 60)

    # 테스트용 사이트맵 URL (실제 URL로 변경하여 사용)
    sitemap_url = "https://example.tistory.com/sitemap.xml"

    print(f"\n📍 테스트 URL: {sitemap_url}")
    print("\n💡 실제 티스토리 블로그 사이트맵으로 테스트하려면")
    print("   test_sitemap.py 파일의 sitemap_url 변수를 수정하세요.")
    print("   예: https://yourblog.tistory.com/sitemap.xml")

    # 1. 사이트맵 다운로드 테스트
    print("\n" + "-" * 60)
    print("1️⃣  사이트맵 다운로드 테스트")
    print("-" * 60)

    xml_content = download_sitemap(sitemap_url)
    if xml_content:
        print(f"✅ 다운로드 성공 (크기: {len(xml_content)} bytes)")
        print(f"📄 XML 미리보기:\n{xml_content[:200]}...")
    else:
        print("❌ 다운로드 실패 (위의 URL이 예시이므로 실패가 정상입니다)")
        print("\n⚠️  실제 테스트를 위해서는 .env 파일을 생성하고")
        print("   SITEMAP_URL을 설정한 후 test_with_env()를 실행하세요.")
        return

    # 2. 사이트맵 타입 확인
    print("\n" + "-" * 60)
    print("2️⃣  사이트맵 타입 확인")
    print("-" * 60)

    if is_sitemap_index(xml_content):
        print("📂 사이트맵 인덱스 파일입니다")

        # 3. 사이트맵 인덱스 파싱
        print("\n" + "-" * 60)
        print("3️⃣  사이트맵 인덱스 파싱")
        print("-" * 60)

        sitemap_urls = parse_sitemap_index(xml_content)
        print(f"✅ {len(sitemap_urls)}개의 하위 사이트맵 발견")
        for idx, url in enumerate(sitemap_urls[:5], 1):  # 처음 5개만 출력
            print(f"   {idx}. {url}")
        if len(sitemap_urls) > 5:
            print(f"   ... 외 {len(sitemap_urls) - 5}개")
    else:
        print("📄 일반 사이트맵 파일입니다")

        # 3. URL 파싱
        print("\n" + "-" * 60)
        print("3️⃣  URL 파싱")
        print("-" * 60)

        urls = parse_sitemap_urls(xml_content)
        print(f"✅ {len(urls)}개의 URL 추출")
        for idx, url_info in enumerate(urls[:5], 1):  # 처음 5개만 출력
            print(f"   {idx}. {url_info['loc']}")
            if url_info['lastmod']:
                print(f"      (수정일: {url_info['lastmod']})")
        if len(urls) > 5:
            print(f"   ... 외 {len(urls) - 5}개")

    # 4. 전체 URL 추출 테스트
    print("\n" + "-" * 60)
    print("4️⃣  전체 URL 추출 테스트")
    print("-" * 60)

    all_urls = get_all_urls_from_sitemap(sitemap_url)
    print(f"✅ 총 {len(all_urls)}개의 URL 추출 완료")

    # 5. 날짜순 정렬 테스트
    print("\n" + "-" * 60)
    print("5️⃣  날짜순 정렬 테스트")
    print("-" * 60)

    sorted_urls = sort_urls_by_date(all_urls, descending=True)
    print(f"✅ 최신순 정렬 완료")
    print("\n📌 최신 URL 5개:")
    for idx, url_info in enumerate(sorted_urls[:5], 1):
        print(f"   {idx}. {url_info['loc']}")
        if url_info['lastmod']:
            print(f"      (수정일: {url_info['lastmod']})")

    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)


def test_with_env():
    """
    .env 파일의 SITEMAP_URL을 사용하여 테스트합니다.
    """
    from dotenv import load_dotenv
    import os

    # .env 파일 로드
    load_dotenv()

    sitemap_url = os.getenv('SITEMAP_URL')

    if not sitemap_url:
        print("❌ .env 파일에 SITEMAP_URL이 설정되지 않았습니다.")
        print("\n💡 .env 파일을 생성하고 다음과 같이 설정하세요:")
        print("   SITEMAP_URL=https://yourblog.tistory.com/sitemap.xml")
        return

    print("=" * 60)
    print("🧪 사이트맵 모듈 테스트 (.env 사용)")
    print("=" * 60)
    print(f"\n📍 사이트맵 URL: {sitemap_url}")

    # 전체 URL 추출
    print("\n🔄 사이트맵 처리 중...\n")
    all_urls = get_all_urls_from_sitemap(sitemap_url)

    if not all_urls:
        print("\n❌ URL 추출 실패")
        return

    print(f"\n✅ 총 {len(all_urls)}개의 URL 추출 완료")

    # 글 페이지만 필터링
    post_urls = filter_post_urls(all_urls)
    print(f"\n📊 필터링 결과:")
    print(f"   전체 URL: {len(all_urls)}개")
    print(f"   글 페이지: {len(post_urls)}개")
    print(f"   기타 페이지: {len(all_urls) - len(post_urls)}개 (모바일, 카테고리, 태그 등)")

    # URL 번호순 정렬 (큰 번호부터)
    sorted_urls = sort_urls_by_number(post_urls, descending=True)

    print("\n📌 최신 글 10개 (URL 번호순):")
    print("-" * 60)
    for idx, url_info in enumerate(sorted_urls[:10], 1):
        print(f"{idx:2d}. {url_info['loc']}")
        if url_info['lastmod']:
            print(f"    📅 {url_info['lastmod']}")

    if len(sorted_urls) > 10:
        print(f"\n... 외 {len(sorted_urls) - 10}개")

    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    # .env 파일이 있으면 .env 사용, 없으면 예시 URL로 테스트
    import os

    if os.path.exists('.env'):
        test_with_env()
    else:
        print("\n💡 .env 파일이 없습니다. 예시 URL로 테스트를 시도합니다.")
        print("   (실패가 정상입니다)\n")
        test_with_example_sitemap()
