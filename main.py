# -*- coding: utf-8 -*-
"""
티스토리 블로그 Google Indexing 자동화 프로그램

이 프로그램은 다음 순서로 실행됩니다:
1. 설정 로드 (.env)
2. 사이트맵에서 URL 추출
3. CSV 파일에 새 URL 추가 (기존 URL은 스킵)
4. PENDING 상태 URL을 Google Indexing API로 전송
5. 결과에 따라 CSV 상태 업데이트 (SUCCESS/FAILED)
6. 로그 저장 및 결과 요약 출력
"""

import os
import sys
import time
from datetime import datetime

# 프로젝트 모듈 임포트
from src.config import load_config, get_domain_from_url
from src.sitemap import (
    get_all_urls_from_sitemap,
    filter_post_urls,
    sort_urls_by_number
)
from src.csv_manager import (
    add_urls_batch,
    get_pending_urls,
    update_url_status,
    get_statistics,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_PENDING
)
from src.indexing import create_indexing_service, submit_urls
from src.logger import (
    setup_logger,
    print_header,
    print_step,
    print_progress,
    print_statistics,
    print_result_summary,
    print_error,
    print_success,
    print_warning,
    print_info
)


# 전체 단계 수
TOTAL_STEPS = 6


def get_csv_path(config: dict) -> str:
    """
    설정에서 CSV 파일 경로를 생성합니다.
    도메인명을 기반으로 data/ 폴더에 저장됩니다.

    Args:
        config: 설정 딕셔너리

    Returns:
        CSV 파일 경로 (예: data/yourblog.tistory.com.csv)
    """
    domain = get_domain_from_url(config['sitemap_url'])
    return os.path.join("data", f"{domain}.csv")


def step1_load_config(logger):
    """
    Step 1: 설정 파일 로드

    .env 파일에서 설정을 로드하고 검증합니다.
    - SITEMAP_URL: 사이트맵 URL (필수)
    - SERVICE_ACCOUNT_FILE: Google 서비스 계정 파일 (필수)
    - DAILY_LIMIT: 일일 인덱싱 제한 (기본 200)

    Returns:
        dict: 설정 딕셔너리 또는 None (실패 시)
    """
    print_step(logger, 1, TOTAL_STEPS, "설정 파일 로드 중...")

    try:
        config = load_config()
        print_success(logger, f"사이트맵: {config['sitemap_url']}")
        print_success(logger, f"일일 제한: {config['daily_limit']}개")
        return config
    except ValueError as e:
        print_error(logger, "설정 파일 로드 실패", e)
        return None
    except Exception as e:
        print_error(logger, "예상치 못한 오류 발생", e)
        return None


def step2_fetch_sitemap(logger, config: dict):
    """
    Step 2: 사이트맵에서 URL 추출

    사이트맵 XML을 다운로드하고 블로그 글 URL만 필터링합니다.
    사이트맵 인덱스인 경우 모든 하위 사이트맵을 순회합니다.

    Args:
        logger: 로거 객체
        config: 설정 딕셔너리

    Returns:
        list: URL 정보 리스트 [{'loc': 'URL', 'lastmod': '날짜'}, ...]
    """
    print_step(logger, 2, TOTAL_STEPS, "사이트맵에서 URL 추출 중...")

    try:
        # 사이트맵에서 모든 URL 가져오기
        all_urls = get_all_urls_from_sitemap(config['sitemap_url'])

        if not all_urls:
            print_warning(logger, "사이트맵에서 URL을 찾을 수 없습니다.")
            return []

        # 블로그 글 URL만 필터링
        post_urls = filter_post_urls(all_urls)

        # URL 번호 기준 정렬 (최신 글부터)
        sorted_urls = sort_urls_by_number(post_urls, descending=True)

        print_success(logger, f"전체 URL: {len(all_urls)}개")
        print_success(logger, f"블로그 글 URL: {len(sorted_urls)}개")

        return sorted_urls

    except Exception as e:
        print_error(logger, "사이트맵 처리 실패", e)
        return []


def step3_sync_csv(logger, csv_path: str, urls: list):
    """
    Step 3: CSV 파일에 URL 동기화

    새로운 URL은 PENDING 상태로 추가합니다.
    이미 존재하는 URL은 건너뜁니다.

    Args:
        logger: 로거 객체
        csv_path: CSV 파일 경로
        urls: URL 정보 리스트

    Returns:
        int: 새로 추가된 URL 수
    """
    print_step(logger, 3, TOTAL_STEPS, "CSV 파일에 URL 동기화 중...")

    try:
        # 새 URL 일괄 추가 (중복은 자동 스킵)
        added_count = add_urls_batch(csv_path, urls)

        if added_count > 0:
            print_success(logger, f"새로 추가된 URL: {added_count}개")
        else:
            print_info(logger, "새로 추가할 URL이 없습니다.")

        # 현재 통계 출력
        stats = get_statistics(csv_path)
        print_statistics(logger, stats, "현재 상태")

        return added_count

    except Exception as e:
        print_error(logger, "CSV 동기화 실패", e)
        return 0


def step4_create_api_service(logger, config: dict):
    """
    Step 4: Google Indexing API 서비스 생성

    Service Account를 사용하여 API 인증을 수행합니다.

    Args:
        logger: 로거 객체
        config: 설정 딕셔너리

    Returns:
        API 서비스 객체 또는 None (실패 시)
    """
    print_step(logger, 4, TOTAL_STEPS, "Google Indexing API 연결 중...")

    try:
        service = create_indexing_service(config['service_account_file'])
        print_success(logger, "API 연결 성공")
        return service
    except Exception as e:
        print_error(logger, "API 연결 실패", e)
        return None


def step5_submit_urls(logger, service, csv_path: str, config: dict):
    """
    Step 5: PENDING URL을 Google Indexing API로 전송

    일일 제한 내에서 PENDING 상태 URL을 인덱싱 요청합니다.
    최대 100개씩 배치로 처리되며, 실패 시 재시도됩니다.

    Args:
        logger: 로거 객체
        service: API 서비스 객체
        csv_path: CSV 파일 경로
        config: 설정 딕셔너리

    Returns:
        tuple: (성공 수, 실패 수)
    """
    print_step(logger, 5, TOTAL_STEPS, "URL 인덱싱 요청 중...")

    # PENDING 상태 URL 가져오기 (일일 제한 적용)
    pending_urls = get_pending_urls(csv_path, limit=config['daily_limit'])

    if not pending_urls:
        print_info(logger, "인덱싱할 URL이 없습니다.")
        return 0, 0

    print_info(logger, f"인덱싱 대상: {len(pending_urls)}개")

    # 결과 카운터
    success_count = 0
    fail_count = 0
    processed = 0
    total = len(pending_urls)

    # 배치 크기 (API 제한: 최대 100개)
    batch_size = 100

    # 배치 단위로 처리
    for i in range(0, total, batch_size):
        batch = pending_urls[i:i + batch_size]
        batch_urls = [item['url'] for item in batch]

        # 콜백 함수: 각 URL 처리 결과를 CSV에 반영
        def on_result(url: str, success: bool, error: str, attempt: int):
            nonlocal success_count, fail_count, processed

            if success:
                # 성공: SUCCESS 상태로 업데이트
                update_url_status(csv_path, url, STATUS_SUCCESS)
                success_count += 1
                logger.debug(f"✓ {url} (시도: {attempt})")
            else:
                # 실패: FAILED 상태로 업데이트, 재시도 횟수 증가
                update_url_status(csv_path, url, STATUS_FAILED, increment_retry=True)
                fail_count += 1
                logger.debug(f"✗ {url}: {error}")

            processed += 1

        # 배치 제출 (재시도 로직 포함)
        try:
            submit_urls(
                service,
                batch_urls,
                max_retry=config['max_retry'],
                retry_delay=config['request_delay'],
                callback=on_result
            )
        except Exception as e:
            print_error(logger, f"배치 제출 실패 (인덱스 {i}~{i+len(batch)})", e)

        # 진행률 표시
        print_progress(logger, processed, total, prefix="인덱싱 진행")

        # 다음 배치 전 잠시 대기 (API Rate Limiting 방지)
        if i + batch_size < total:
            time.sleep(config['request_delay'])

    return success_count, fail_count


def step6_print_summary(logger, csv_path: str, success_count: int, fail_count: int, elapsed_time: float):
    """
    Step 6: 최종 결과 요약 출력

    Args:
        logger: 로거 객체
        csv_path: CSV 파일 경로
        success_count: 성공한 URL 수
        fail_count: 실패한 URL 수
        elapsed_time: 소요 시간 (초)
    """
    print_step(logger, 6, TOTAL_STEPS, "결과 요약 중...")

    # 실행 결과 요약
    print_result_summary(logger, success_count, fail_count, elapsed_time)

    # 최종 통계
    stats = get_statistics(csv_path)
    print_statistics(logger, stats, "최종 상태")


def main():
    """
    메인 함수: 전체 프로세스를 순차적으로 실행합니다.

    실행 순서:
    1. 설정 로드
    2. 사이트맵 URL 추출
    3. CSV 동기화
    4. API 서비스 생성
    5. URL 인덱싱 요청
    6. 결과 요약 출력
    """
    # 시작 시간 기록
    start_time = time.time()

    # 로거 설정
    logger = setup_logger()

    # 프로그램 시작 메시지
    print_header(logger, "티스토리 블로그 Google Indexing 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: 설정 로드
    config = step1_load_config(logger)
    if not config:
        logger.error("프로그램을 종료합니다.")
        sys.exit(1)

    # CSV 파일 경로 설정
    csv_path = get_csv_path(config)
    logger.info(f"CSV 파일: {csv_path}")

    # Step 2: 사이트맵 URL 추출
    print_header(logger, "사이트맵 처리")
    urls = step2_fetch_sitemap(logger, config)
    if not urls:
        logger.warning("URL이 없어 프로그램을 종료합니다.")
        sys.exit(0)

    # Step 3: CSV 동기화
    print_header(logger, "CSV 동기화")
    step3_sync_csv(logger, csv_path, urls)

    # Step 4: API 서비스 생성
    print_header(logger, "Google Indexing API 연동")
    service = step4_create_api_service(logger, config)
    if not service:
        logger.error("API 서비스 생성 실패로 프로그램을 종료합니다.")
        sys.exit(1)

    # Step 5: URL 인덱싱
    print_header(logger, "URL 인덱싱")
    success_count, fail_count = step5_submit_urls(logger, service, csv_path, config)

    # 소요 시간 계산
    elapsed_time = time.time() - start_time

    # Step 6: 결과 요약
    print_header(logger, "실행 완료")
    step6_print_summary(logger, csv_path, success_count, fail_count, elapsed_time)

    # 완료 메시지
    print_success(logger, "프로그램이 정상적으로 종료되었습니다.")


if __name__ == "__main__":
    main()
