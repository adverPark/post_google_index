# -*- coding: utf-8 -*-
"""
Google Indexing API 연동 모듈

Google Indexing API를 사용하여 URL을 인덱싱하는 기능을 제공합니다.
Service Account 인증을 사용하며, 배치 인덱싱을 지원합니다.
"""

import time
import json
from typing import Dict, List, Tuple, Optional, Callable
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Google Indexing API 설정
SCOPES = ["https://www.googleapis.com/auth/indexing"]
API_SERVICE_NAME = "indexing"
API_VERSION = "v3"


def create_indexing_service(service_account_file: str):
    """
    Google Indexing API 서비스 객체를 생성합니다.

    Service Account JSON 파일을 사용하여 인증하고,
    Google Indexing API와 통신할 수 있는 서비스 객체를 반환합니다.

    Args:
        service_account_file: Service Account JSON 파일 경로

    Returns:
        googleapiclient.discovery.Resource: Indexing API 서비스 객체

    Raises:
        Exception: 인증 실패 시 예외 발생

    Example:
        >>> service = create_indexing_service('./service-account.json')
        >>> # 이제 service 객체를 사용하여 API 호출 가능
    """
    try:
        # Service Account 자격 증명 생성
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )

        # Indexing API 서비스 빌드
        service = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials
        )

        return service

    except Exception as e:
        raise Exception(f"Indexing API 서비스 생성 실패: {str(e)}")


def submit_urls(
    service,
    urls: List[str],
    max_retry: int = 3,
    retry_delay: float = 1.0,
    callback: Optional[Callable[[str, bool, Optional[str], int], None]] = None
) -> Dict[str, Tuple[bool, Optional[str], int]]:
    """
    URL을 배치로 인덱싱 요청합니다. (재시도 로직 포함)

    1개부터 최대 100개의 URL을 배치로 제출합니다.
    실패한 URL은 자동으로 재시도됩니다.

    Args:
        service: Indexing API 서비스 객체
        urls: 인덱싱할 URL 리스트 (1~100개)
        max_retry: 최대 재시도 횟수 (기본값: 3)
        retry_delay: 재시도 간 대기 시간 (초, 기본값: 1.0)
        callback: 각 URL 처리 후 호출될 콜백 함수 (선택사항)
                 함수 시그니처: callback(url, success, error, attempt)

    Returns:
        Dict[str, Tuple[bool, Optional[str], int]]: URL별 결과 딕셔너리
            - Key: URL
            - Value: (성공 여부, 에러 메시지, 시도 횟수)

    Raises:
        ValueError: URL이 100개를 초과하거나 빈 리스트인 경우

    Example:
        # 단일 URL 제출
        >>> service = create_indexing_service('./service-account.json')
        >>> results = submit_urls(service, ["https://example.com/post1"])
        >>> url, (success, error, attempts) = list(results.items())[0]
        >>> print(f"성공: {success}, 시도 횟수: {attempts}")

        # 여러 URL 제출
        >>> urls = [
        ...     "https://example.com/post1",
        ...     "https://example.com/post2",
        ...     "https://example.com/post3"
        ... ]
        >>> results = submit_urls(service, urls, max_retry=3)
        >>> for url, (success, error, attempts) in results.items():
        ...     if success:
        ...         print(f"✓ {url} (시도: {attempts})")
        ...     else:
        ...         print(f"✗ {url}: {error}")

        # 콜백 함수 사용
        >>> def progress_callback(url, success, error, attempt):
        ...     print(f"[시도 {attempt}] {url}: {'성공' if success else error}")
        >>> results = submit_urls(service, urls, callback=progress_callback)
    """
    if not urls:
        raise ValueError("URL 리스트가 비어있습니다.")

    if len(urls) > 100:
        raise ValueError("배치 요청은 최대 100개의 URL만 허용됩니다.")

    # 최종 결과 저장 (url -> (success, error, attempts))
    final_results = {}

    # 재시도할 URL 리스트 초기화
    urls_to_retry = list(urls)
    attempt = 0

    # 최대 재시도 횟수만큼 반복
    while urls_to_retry and attempt < max_retry:
        attempt += 1

        # 배치 요청 실행
        batch_results = _execute_batch_request(service, urls_to_retry)

        # 결과 처리 및 재시도 목록 업데이트
        next_retry_urls = []

        for url, (success, error) in batch_results.items():
            if success:
                # 성공: 최종 결과에 저장
                final_results[url] = (True, None, attempt)

                # 콜백 호출
                if callback:
                    callback(url, True, None, attempt)
            else:
                # 실패: 최종 시도가 아니면 재시도 목록에 추가
                if attempt < max_retry:
                    next_retry_urls.append(url)
                else:
                    # 최종 실패: 결과에 저장
                    final_results[url] = (False, error, attempt)

                    # 콜백 호출
                    if callback:
                        callback(url, False, error, attempt)

        # 재시도할 URL 업데이트
        urls_to_retry = next_retry_urls

        # 재시도가 필요하고 마지막 시도가 아니면 대기
        if urls_to_retry and attempt < max_retry:
            time.sleep(retry_delay)

    return final_results


def _execute_batch_request(
    service,
    urls: List[str]
) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    배치 요청을 실행합니다. (내부 함수)

    이 함수는 submit_urls에서만 호출되며, 재시도 로직 없이
    단순히 배치 요청만 실행합니다.

    Args:
        service: Indexing API 서비스 객체
        urls: 인덱싱할 URL 리스트

    Returns:
        Dict[str, Tuple[bool, Optional[str]]]: URL별 결과
            - Key: URL
            - Value: (성공 여부, 에러 메시지)
    """
    # 결과 저장용 딕셔너리
    results = {}

    # 배치 요청 핸들러 정의
    def batch_callback(request_id, response, exception):
        """
        배치 요청의 각 응답을 처리하는 콜백 함수입니다.

        Args:
            request_id: 요청 ID (URL)
            response: 성공 시 응답 객체 (사용하지 않음)
            exception: 실패 시 예외 객체
        """
        url = request_id
        _ = response  # 사용하지 않지만 콜백 시그니처에 필요

        if exception is not None:
            # 에러 발생
            if isinstance(exception, HttpError):
                try:
                    error_content = json.loads(exception.content.decode())
                    error_message = error_content.get('error', {}).get('message', str(exception))

                    # 상태 코드별 에러 메시지 보강
                    status = exception.resp.status
                    if status == 403:
                        error_message = f"권한 없음 (403): {error_message}"
                    elif status == 429:
                        error_message = f"할당량 초과 (429): {error_message}"
                    elif status == 400:
                        error_message = f"잘못된 요청 (400): {error_message}"
                except:
                    error_message = str(exception)
            else:
                error_message = str(exception)

            results[url] = (False, error_message)
        else:
            # 성공
            results[url] = (True, None)

    # 배치 요청 생성
    batch = service.new_batch_http_request(callback=batch_callback)

    # 각 URL을 배치에 추가
    for url in urls:
        body = {
            "url": url,
            "type": "URL_UPDATED"
        }
        # request_id에 URL을 전달하여 콜백에서 식별 가능하도록 함
        batch.add(
            service.urlNotifications().publish(body=body),
            request_id=url
        )

    # 배치 실행
    batch.execute()

    return results


def get_url_status(service, url: str) -> Optional[Dict]:
    """
    특정 URL의 인덱싱 상태를 조회합니다.

    Google에 이전에 제출한 URL의 현재 상태를 확인합니다.

    Args:
        service: Indexing API 서비스 객체
        url: 상태를 조회할 URL

    Returns:
        Optional[Dict]: URL 상태 정보 또는 None
            - notificationMetadata: 알림 메타데이터
            - urlNotificationMetadata: URL 알림 메타데이터

    Example:
        >>> service = create_indexing_service('./service-account.json')
        >>> status = get_url_status(service, "https://example.com/post")
        >>> if status:
        ...     print(f"마지막 업데이트: {status.get('latestUpdate')}")
    """
    try:
        response = service.urlNotifications().getMetadata(url=url).execute()
        return response
    except HttpError as e:
        if e.resp.status == 404:
            # URL이 제출된 적 없음
            return None
        else:
            raise e
