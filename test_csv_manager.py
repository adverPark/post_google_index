"""
CSV 관리자 테스트 스크립트

src/csv_manager.py의 모든 기능을 테스트합니다.
"""

import os
import sys
from pathlib import Path

# src 모듈을 import하기 위한 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from src.csv_manager import (
    read_csv,
    write_csv,
    get_url_status,
    add_url,
    update_url_status,
    get_pending_urls,
    add_urls_batch,
    get_statistics,
    STATUS_PENDING,
    STATUS_SUCCESS,
    STATUS_FAILED
)


def test_csv_manager():
    """CSV 관리자 모든 기능 테스트"""

    # 테스트용 CSV 파일 경로
    test_csv = 'data/test_urls.csv'

    print("=" * 60)
    print("CSV 관리자 테스트 시작")
    print("=" * 60)

    # 기존 테스트 파일 삭제 (깨끗한 상태로 시작)
    if os.path.exists(test_csv):
        os.remove(test_csv)
        print(f"🗑️  기존 테스트 파일 삭제: {test_csv}\n")

    # ===== 테스트 1: 단일 URL 추가 =====
    print("\n📝 테스트 1: 단일 URL 추가")
    print("-" * 60)

    url1 = 'https://example.tistory.com/1'
    url2 = 'https://example.tistory.com/2'

    result1 = add_url(test_csv, url1, '2025-01-01T10:00:00+09:00')
    result2 = add_url(test_csv, url2, '2025-01-02T10:00:00+09:00')

    print(f"URL1 추가 결과: {result1}")
    print(f"URL2 추가 결과: {result2}")

    # 중복 추가 테스트
    result3 = add_url(test_csv, url1)
    print(f"URL1 중복 추가 결과 (False 예상): {result3}")


    # ===== 테스트 2: URL 상태 확인 =====
    print("\n\n🔍 테스트 2: URL 상태 확인")
    print("-" * 60)

    status1 = get_url_status(test_csv, url1)
    status2 = get_url_status(test_csv, url2)
    status3 = get_url_status(test_csv, 'https://example.tistory.com/999')

    print(f"URL1 상태: {status1} (PENDING 예상)")
    print(f"URL2 상태: {status2} (PENDING 예상)")
    print(f"존재하지 않는 URL 상태: {status3} (None 예상)")


    # ===== 테스트 3: URL 상태 업데이트 =====
    print("\n\n🔄 테스트 3: URL 상태 업데이트")
    print("-" * 60)

    # URL1을 SUCCESS로 변경
    result = update_url_status(test_csv, url1, STATUS_SUCCESS)
    print(f"URL1 상태 업데이트 (SUCCESS): {result}")

    # URL2를 FAILED로 변경하고 재시도 횟수 증가
    result = update_url_status(test_csv, url2, STATUS_FAILED, increment_retry=True)
    print(f"URL2 상태 업데이트 (FAILED, retry++): {result}")

    # 변경 확인
    status1 = get_url_status(test_csv, url1)
    status2 = get_url_status(test_csv, url2)
    print(f"URL1 변경 후 상태: {status1} (SUCCESS 예상)")
    print(f"URL2 변경 후 상태: {status2} (FAILED 예상)")


    # ===== 테스트 4: 배치 URL 추가 =====
    print("\n\n📦 테스트 4: 배치 URL 추가")
    print("-" * 60)

    # 사이트맵에서 추출한 형태의 URL 목록
    batch_urls = [
        {'loc': 'https://example.tistory.com/3', 'lastmod': '2025-01-03T10:00:00+09:00'},
        {'loc': 'https://example.tistory.com/4', 'lastmod': '2025-01-04T10:00:00+09:00'},
        {'loc': 'https://example.tistory.com/5', 'lastmod': '2025-01-05T10:00:00+09:00'},
        {'loc': 'https://example.tistory.com/1', 'lastmod': '2025-01-01T10:00:00+09:00'},  # 중복
    ]

    added_count = add_urls_batch(test_csv, batch_urls)
    print(f"추가된 URL 개수: {added_count} (3개 예상, 1개는 중복)")


    # ===== 테스트 5: PENDING URL 필터링 =====
    print("\n\n📋 테스트 5: PENDING URL 필터링")
    print("-" * 60)

    pending_urls = get_pending_urls(test_csv)
    print(f"PENDING 상태 URL 개수: {len(pending_urls)}")
    print("PENDING URL 목록:")
    for url_info in pending_urls:
        print(f"  - {url_info['url']} (retry: {url_info.get('retry_count', 0)})")

    # limit 테스트
    pending_urls_limited = get_pending_urls(test_csv, limit=2)
    print(f"\nLimit=2 적용 시 개수: {len(pending_urls_limited)}")


    # ===== 테스트 6: 통계 정보 =====
    print("\n\n📊 테스트 6: 통계 정보")
    print("-" * 60)

    stats = get_statistics(test_csv)
    print(f"전체 URL: {stats['total']}")
    print(f"PENDING: {stats['pending']}")
    print(f"SUCCESS: {stats['success']}")
    print(f"FAILED: {stats['failed']}")


    # ===== 테스트 7: CSV 파일 직접 읽기 =====
    print("\n\n📖 테스트 7: CSV 파일 내용 확인")
    print("-" * 60)

    all_data = read_csv(test_csv)
    print(f"총 {len(all_data)}개 항목:")
    for idx, row in enumerate(all_data, 1):
        print(f"\n{idx}. URL: {row['url']}")
        print(f"   상태: {row['status']}")
        print(f"   최종 수정일: {row['lastmod']}")
        print(f"   생성일: {row['created_at']}")
        print(f"   업데이트일: {row['updated_at']}")
        print(f"   재시도 횟수: {row['retry_count']}")


    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)
    print(f"\n테스트 파일 위치: {test_csv}")
    print("파일을 확인하여 CSV 형식을 검증하세요.\n")


if __name__ == '__main__':
    test_csv_manager()
