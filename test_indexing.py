# -*- coding: utf-8 -*-
"""
Google Indexing API 테스트 스크립트

indexing.py 모듈의 기능을 테스트합니다.
실제 API 호출을 수행하므로 Service Account 파일과 권한이 필요합니다.
"""

import sys
from src.config import load_config
from src.indexing import (
    create_indexing_service,
    submit_urls,
    get_url_status
)


def test_service_creation():
    """Service Account 인증 및 서비스 생성 테스트"""
    print("=" * 60)
    print("테스트 1: Indexing API 서비스 생성")
    print("=" * 60)

    try:
        config = load_config()
        service = create_indexing_service(config['service_account_file'])
        print("✓ 서비스 생성 성공!")
        print(f"  - Service Account 파일: {config['service_account_file']}")
        return service, config
    except Exception as e:
        print(f"✗ 서비스 생성 실패: {e}")
        return None, None


def test_single_url_submission(service, config):
    """단일 URL 인덱싱 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 단일 URL 인덱싱")
    print("=" * 60)

    if not service:
        print("⊘ 서비스가 생성되지 않아 테스트를 건너뜁니다.")
        return

    # 테스트용 URL (실제 사이트의 URL로 변경하세요)
    test_url = "https://luluj-australia.tistory.com/1"

    print(f"\n테스트 URL: {test_url}")
    print(f"최대 재시도 횟수: {config['max_retry']}")

    # 진행 상황 콜백
    def progress_callback(url, success, error, attempt):
        if success:
            print(f"  [시도 {attempt}] ✓ 인덱싱 성공")
        else:
            print(f"  [시도 {attempt}] ✗ 실패: {error}")

    try:
        # 단일 URL을 리스트로 전달
        results = submit_urls(
            service,
            [test_url],
            max_retry=config['max_retry'],
            retry_delay=config['request_delay'],
            callback=progress_callback
        )

        # 결과 출력
        url, (success, error, attempts) = list(results.items())[0]
        print(f"\n최종 결과:")
        print(f"  - 시도 횟수: {attempts}")
        print(f"  - 성공 여부: {success}")
        if not success:
            print(f"  - 에러 메시지: {error}")

    except Exception as e:
        print(f"✗ 예외 발생: {e}")


def test_batch_submission(service, config):
    """배치 URL 인덱싱 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 배치 URL 인덱싱")
    print("=" * 60)

    if not service:
        print("⊘ 서비스가 생성되지 않아 테스트를 건너뜁니다.")
        return

    # 테스트용 URL 리스트 (실제 사이트의 URL로 변경하세요)
    test_urls = [
        "https://luluj-australia.tistory.com/2",
        "https://luluj-australia.tistory.com/3",
        "https://luluj-australia.tistory.com/4",
    ]

    print(f"\n테스트 URL 개수: {len(test_urls)}")
    print(f"최대 재시도 횟수: {config['max_retry']}")
    print()

    # 진행 상황 콜백
    def progress_callback(url, success, error, attempt):
        if success:
            print(f"  [시도 {attempt}] ✓ {url}")
        else:
            if attempt < config['max_retry']:
                print(f"  [시도 {attempt}] ⟳ {url}: {error} (재시도 예정)")
            else:
                print(f"  [시도 {attempt}] ✗ {url}: {error}")

    try:
        results = submit_urls(
            service,
            test_urls,
            max_retry=config['max_retry'],
            retry_delay=config['request_delay'],
            callback=progress_callback
        )

        # 결과 요약
        success_count = sum(1 for success, _, _ in results.values() if success)
        fail_count = len(results) - success_count

        print(f"\n결과 요약:")
        print(f"  - 성공: {success_count}/{len(test_urls)}")
        print(f"  - 실패: {fail_count}/{len(test_urls)}")

        # 실패한 URL 상세 정보
        if fail_count > 0:
            print(f"\n실패한 URL 상세:")
            for url, (success, error, attempts) in results.items():
                if not success:
                    print(f"  - {url}")
                    print(f"    시도 횟수: {attempts}")
                    print(f"    에러: {error}")

    except Exception as e:
        print(f"✗ 예외 발생: {e}")


def test_large_batch_submission(service, config):
    """대량 배치 URL 인덱싱 테스트 (50개)"""
    print("\n" + "=" * 60)
    print("테스트 4: 대량 배치 URL 인덱싱 (50개)")
    print("=" * 60)

    if not service:
        print("⊘ 서비스가 생성되지 않아 테스트를 건너뜁니다.")
        return

    # 50개 URL 생성 (실제 사이트의 URL로 변경하세요)
    test_urls = [f"https://luluj-australia.tistory.com/{i}" for i in range(10, 60)]

    print(f"\n테스트 URL 개수: {len(test_urls)}")
    print(f"최대 재시도 횟수: {config['max_retry']}")
    print("\n진행 상황:")

    # 간단한 진행 상황 콜백
    success_count = 0
    fail_count = 0

    def progress_callback(url, success, error, attempt):
        nonlocal success_count, fail_count
        if success:
            success_count += 1
            print(".", end="", flush=True)
        else:
            if attempt >= config['max_retry']:
                fail_count += 1
                print("X", end="", flush=True)

    try:
        results = submit_urls(
            service,
            test_urls,
            max_retry=config['max_retry'],
            retry_delay=config['request_delay'],
            callback=progress_callback
        )

        print()  # 줄바꿈
        print(f"\n결과 요약:")
        print(f"  - 성공: {success_count}/{len(test_urls)}")
        print(f"  - 실패: {fail_count}/{len(test_urls)}")

    except Exception as e:
        print(f"\n✗ 예외 발생: {e}")


def test_get_url_status(service):
    """URL 상태 조회 테스트"""
    print("\n" + "=" * 60)
    print("테스트 5: URL 상태 조회")
    print("=" * 60)

    if not service:
        print("⊘ 서비스가 생성되지 않아 테스트를 건너뜁니다.")
        return

    # 이전에 제출한 URL로 테스트
    test_url = "https://luluj-australia.tistory.com/1"

    print(f"\n조회 URL: {test_url}")

    try:
        status = get_url_status(service, test_url)

        if status:
            print("✓ 상태 조회 성공!")
            print(f"\n응답 내용:")
            import json
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print("⊘ 해당 URL은 아직 제출된 적이 없습니다.")

    except Exception as e:
        print(f"✗ 예외 발생: {e}")


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("Google Indexing API 테스트 시작")
    print("=" * 60)
    print("\n⚠️  주의사항:")
    print("  1. Service Account JSON 파일이 필요합니다")
    print("  2. Service Account에 권한이 부여되어 있어야 합니다")
    print("  3. 실제 API 호출이 발생하므로 할당량이 소비됩니다")
    print("  4. 테스트 URL은 실제 사이트의 URL로 변경하세요")
    print()

    # 사용자 확인
    response = input("테스트를 계속하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("\n테스트를 취소했습니다.")
        sys.exit(0)

    # 테스트 실행
    service, config = test_service_creation()

    if service and config:
        # 기본 테스트
        test_single_url_submission(service, config)
        test_batch_submission(service, config)

        # 대량 테스트 (선택)
        print("\n" + "=" * 60)
        response = input("\n대량 배치 테스트(50개 URL)를 실행하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            test_large_batch_submission(service, config)

        # 상태 조회 테스트
        test_get_url_status(service)

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
