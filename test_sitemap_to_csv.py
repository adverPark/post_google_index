"""
사이트맵 → CSV 통합 테스트

.env 파일에서 SITEMAP_URL을 읽어서
실제 사이트맵을 다운로드하고 CSV 파일을 생성하는 통합 테스트입니다.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# src 모듈을 import하기 위한 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from src.sitemap import (
    get_all_urls_from_sitemap,
    filter_post_urls,
    sort_urls_by_number
)
from src.csv_manager import (
    add_urls_batch,
    get_statistics,
    read_csv
)


def test_sitemap_to_csv():
    """사이트맵에서 CSV로 전체 플로우 테스트"""

    print("=" * 70)
    print("사이트맵 → CSV 통합 테스트")
    print("=" * 70)

    # ===== Step 1: .env 파일 로드 =====
    print("\n📝 Step 1: .env 파일 로드")
    print("-" * 70)

    # .env 파일 로드
    load_dotenv()

    # 사이트맵 URL 읽기
    sitemap_url = os.getenv('SITEMAP_URL')

    if not sitemap_url:
        print("❌ .env 파일에 SITEMAP_URL이 설정되지 않았습니다!")
        return

    print(f"✅ 사이트맵 URL: {sitemap_url}")


    # ===== Step 2: 사이트맵 다운로드 및 파싱 =====
    print("\n\n📥 Step 2: 사이트맵 다운로드 및 URL 추출")
    print("-" * 70)

    # 사이트맵에서 모든 URL 추출
    all_urls = get_all_urls_from_sitemap(sitemap_url)

    if not all_urls:
        print("❌ 사이트맵에서 URL을 추출하지 못했습니다!")
        return

    print(f"\n📊 총 추출된 URL 개수: {len(all_urls)}")


    # ===== Step 3: 블로그 글 페이지만 필터링 =====
    print("\n\n🔍 Step 3: 블로그 글 페이지 필터링")
    print("-" * 70)

    # 카테고리, 태그, 메인 페이지 등을 제외하고 블로그 글만 필터링
    post_urls = filter_post_urls(all_urls)

    print(f"✅ 필터링된 블로그 글 개수: {len(post_urls)}")

    if post_urls:
        print(f"\n📌 필터링된 URL 예시 (처음 5개):")
        for i, url_info in enumerate(post_urls[:5], 1):
            print(f"  {i}. {url_info['loc']}")
            print(f"     수정일: {url_info['lastmod']}")


    # ===== Step 4: URL 번호순 정렬 (최신글부터) =====
    print("\n\n🔢 Step 4: URL 번호순 정렬 (큰 번호부터)")
    print("-" * 70)

    # URL 번호순으로 정렬 (큰 번호가 최신 글)
    sorted_urls = sort_urls_by_number(post_urls, descending=True)

    print(f"✅ 정렬 완료")

    if sorted_urls:
        print(f"\n📌 정렬된 URL (처음 5개):")
        for i, url_info in enumerate(sorted_urls[:5], 1):
            print(f"  {i}. {url_info['loc']}")


    # ===== Step 5: CSV 파일 생성 =====
    print("\n\n💾 Step 5: CSV 파일 생성")
    print("-" * 70)

    # 실제 운영용 CSV 파일 경로
    csv_path = 'data/urls.csv'

    print(f"📁 CSV 파일 경로: {csv_path}")

    # 기존 CSV 파일이 있는지 확인
    if os.path.exists(csv_path):
        print(f"ℹ️  기존 CSV 파일 존재 (새로운 URL만 추가됩니다)")
        existing_data = read_csv(csv_path)
        print(f"📊 기존 CSV 항목 수: {len(existing_data)}")
    else:
        print(f"ℹ️  새로운 CSV 파일 생성")

    # 사이트맵 URL을 CSV에 배치 추가
    added_count = add_urls_batch(csv_path, sorted_urls)

    print(f"\n✅ CSV 파일 업데이트 완료!")
    print(f"   새로 추가된 URL: {added_count}개")


    # ===== Step 6: CSV 통계 확인 =====
    print("\n\n📊 Step 6: CSV 통계 정보")
    print("-" * 70)

    stats = get_statistics(csv_path)

    print(f"전체 URL:        {stats['total']:>5}개")
    print(f"PENDING (대기):  {stats['pending']:>5}개")
    print(f"SUCCESS (성공):  {stats['success']:>5}개")
    print(f"FAILED (실패):   {stats['failed']:>5}개")


    # ===== Step 7: 샘플 데이터 확인 =====
    print("\n\n📋 Step 7: CSV 데이터 샘플 (처음 3개)")
    print("-" * 70)

    all_data = read_csv(csv_path)

    for i, row in enumerate(all_data[:3], 1):
        print(f"\n{i}. {row['url']}")
        print(f"   상태: {row['status']}")
        print(f"   최종 수정일: {row['lastmod']}")
        print(f"   생성일: {row['created_at']}")
        print(f"   재시도 횟수: {row['retry_count']}")


    # ===== 완료 =====
    print("\n" + "=" * 70)
    print("✅ 사이트맵 → CSV 통합 테스트 완료!")
    print("=" * 70)

    print(f"\n📁 생성된 CSV 파일: {csv_path}")
    print(f"📊 총 {stats['total']}개 URL이 CSV에 저장되었습니다.")
    print(f"🔄 다음 단계: Google Indexing API로 PENDING 상태 URL 전송\n")


if __name__ == '__main__':
    # python-dotenv 패키지 확인
    try:
        import dotenv
        test_sitemap_to_csv()
    except ImportError:
        print("❌ python-dotenv 패키지가 설치되지 않았습니다!")
        print("   설치: uv add python-dotenv")
