# -*- coding: utf-8 -*-
"""
설정 관리 모듈

.env 파일에서 환경 변수를 로드하고 프로그램 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv


def load_config():
    """
    .env 파일에서 설정을 로드합니다.

    Returns:
        dict: 설정 값들을 담은 딕셔너리
            - sitemap_url: 티스토리 사이트맵 URL
            - service_account_file: Google Service Account JSON 파일 경로
            - max_retry: 최대 재시도 횟수
            - request_delay: API 요청 간 지연 시간 (초)
            - daily_limit: 일일 최대 인덱싱 요청 수

    Raises:
        ValueError: 필수 설정이 누락된 경우
    """
    # .env 파일 로드 (기존 환경 변수 덮어쓰기)
    load_dotenv(override=True)

    # 필수 설정값 가져오기
    sitemap_url = os.getenv('SITEMAP_URL')
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')

    # 필수 설정값 검증
    if not sitemap_url:
        raise ValueError("SITEMAP_URL이 .env 파일에 설정되어 있지 않습니다.")

    if not service_account_file:
        raise ValueError("SERVICE_ACCOUNT_FILE이 .env 파일에 설정되어 있지 않습니다.")

    # Service Account 파일 존재 여부 확인
    if not os.path.exists(service_account_file):
        raise ValueError(f"Service Account 파일을 찾을 수 없습니다: {service_account_file}")

    # 선택적 설정값 (기본값 포함)
    max_retry = int(os.getenv('MAX_RETRY', '3'))
    request_delay = float(os.getenv('REQUEST_DELAY', '1'))
    daily_limit = int(os.getenv('DAILY_LIMIT', '200'))

    # 설정 딕셔너리 반환
    config = {
        'sitemap_url': sitemap_url,
        'service_account_file': service_account_file,
        'max_retry': max_retry,
        'request_delay': request_delay,
        'daily_limit': daily_limit,
    }

    return config


def get_domain_from_url(url):
    """
    URL에서 도메인명을 추출합니다.

    Args:
        url: 사이트맵 URL (예: https://yourblog.tistory.com/sitemap.xml)

    Returns:
        str: 도메인명 (예: yourblog.tistory.com)
    """
    # URL에서 프로토콜 제거
    if '://' in url:
        url = url.split('://')[1]

    # 경로 제거 (첫 번째 / 이전까지만)
    domain = url.split('/')[0]

    return domain
