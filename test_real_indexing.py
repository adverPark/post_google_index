# -*- coding: utf-8 -*-
"""
실제 사이트맵 기반 인덱싱 테스트

.env의 실제 사이트맵을 다운로드하여 10개 URL을 인덱싱합니다.
"""

from src.config import load_config
from src.sitemap import download_sitemap, parse_sitemap_urls
from src.indexing import create_indexing_service, submit_urls


def main():
    print("=" * 60)
    print("실제 사이트맵 기반 인덱싱 테스트")
    print("=" * 60)

    # 1. 설정 로드
    print("\n[1단계] 설정 로드")
    try:
        config = load_config()
        print(f"✓ 사이트맵 URL: {config['sitemap_url']}")
        print(f"✓ Service Account: {config['service_account_file']}")
        print(f"✓ 최대 재시도: {config['max_retry']}")
        print(f"✓ 일일 제한: {config['daily_limit']}")
    except Exception as e:
        print(f"✗ 설정 로드 실패: {e}")
        return

    # 2. 사이트맵 다운로드
    print("\n[2단계] 사이트맵 다운로드")
    try:
        xml_content = download_sitemap(config['sitemap_url'])
        print(f"✓ 사이트맵 다운로드 성공")
    except Exception as e:
        print(f"✗ 사이트맵 다운로드 실패: {e}")
        return

    # 3. URL 파싱
    print("\n[3단계] URL 파싱")
    try:
        all_urls = parse_sitemap_urls(xml_content)
        print(f"✓ 총 {len(all_urls)}개 URL 추출")

        # 처음 10개만 선택 (최대 daily_limit 고려)
        limit = min(10, config['daily_limit'])
        test_urls = [url_info['loc'] for url_info in all_urls[:limit]]
        print(f"✓ 테스트용 {len(test_urls)}개 URL 선택")

        # 선택된 URL 출력
        print("\n선택된 URL:")
        for i, url in enumerate(test_urls, 1):
            print(f"  {i}. {url}")

    except Exception as e:
        print(f"✗ URL 파싱 실패: {e}")
        return

    # 4. Indexing API 서비스 생성
    print("\n[4단계] Indexing API 인증")
    try:
        service = create_indexing_service(config['service_account_file'])
        print("✓ 인증 성공")
    except Exception as e:
        print(f"✗ 인증 실패: {e}")
        return

    # 5. 인덱싱 실행
    print("\n[5단계] URL 인덱싱 시작")
    print(f"최대 재시도 횟수: {config['max_retry']}")
    print(f"재시도 간 대기 시간: {config['request_delay']}초")
    print()

    # 진행 상황 출력 콜백
    def progress_callback(url, success, error, attempt):
        if success:
            print(f"  [시도 {attempt}] ✓ {url}")
        else:
            if attempt < config['max_retry']:
                print(f"  [시도 {attempt}] ⟳ 재시도 예정: {url}")
                print(f"           에러: {error}")
            else:
                print(f"  [시도 {attempt}] ✗ 최종 실패: {url}")
                print(f"           에러: {error}")

    try:
        results = submit_urls(
            service,
            test_urls,
            max_retry=config['max_retry'],
            retry_delay=config['request_delay'],
            callback=progress_callback
        )

        # 6. 결과 요약
        print("\n" + "=" * 60)
        print("결과 요약")
        print("=" * 60)

        success_count = sum(1 for success, _, _ in results.values() if success)
        fail_count = len(results) - success_count

        print(f"\n전체: {len(test_urls)}개")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")

        # 성공한 URL 목록
        if success_count > 0:
            print(f"\n✓ 성공한 URL ({success_count}개):")
            for url, (success, _, attempts) in results.items():
                if success:
                    print(f"  - {url} (시도: {attempts})")

        # 실패한 URL 목록
        if fail_count > 0:
            print(f"\n✗ 실패한 URL ({fail_count}개):")
            for url, (success, error, attempts) in results.items():
                if not success:
                    print(f"  - {url}")
                    print(f"    시도 횟수: {attempts}")
                    print(f"    에러: {error}")

        print("\n" + "=" * 60)
        print("테스트 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 인덱싱 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
