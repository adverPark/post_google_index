# -*- coding: utf-8 -*-
"""
로깅 및 진행 상황 표시 모듈

이 모듈은 프로그램 실행 중 발생하는 이벤트를 로그 파일과 콘솔에 출력합니다.
로그 파일은 logs/ 폴더에 날짜별로 저장됩니다.
"""

import os
import logging
from datetime import datetime
from typing import Optional


# 로그 디렉토리 경로
LOG_DIR = "logs"


def setup_logger(log_dir: str = LOG_DIR) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.

    로그는 두 곳에 출력됩니다:
    1. 콘솔 (INFO 레벨 이상)
    2. 파일 (DEBUG 레벨 이상, logs/YYYY-MM-DD.log)

    Args:
        log_dir: 로그 파일이 저장될 디렉토리 (기본값: "logs")

    Returns:
        logging.Logger: 설정된 로거 객체

    Example:
        >>> logger = setup_logger()
        >>> logger.info("프로그램 시작")
        >>> logger.error("에러 발생", exc_info=True)
    """
    # 로그 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 오늘 날짜로 로그 파일명 생성
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.log")

    # 로거 생성 (기존 로거가 있으면 재사용)
    logger = logging.getLogger("post_google_index")

    # 이미 핸들러가 설정되어 있으면 스킵 (중복 방지)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 파일 핸들러 설정 (DEBUG 레벨 이상 모두 기록)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # 콘솔 핸들러 설정 (INFO 레벨 이상만 출력)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def print_header(logger: logging.Logger, title: str) -> None:
    """
    섹션 헤더를 출력합니다.

    Args:
        logger: 로거 객체
        title: 섹션 제목

    Example:
        >>> print_header(logger, "사이트맵 다운로드")
        # 출력:
        # ═══════════════════════════════════════════════════════
        # 📌 사이트맵 다운로드
        # ═══════════════════════════════════════════════════════
    """
    separator = "═" * 55
    logger.info("")
    logger.info(separator)
    logger.info(f"📌 {title}")
    logger.info(separator)


def print_step(logger: logging.Logger, step: int, total: int, message: str) -> None:
    """
    단계별 진행 상황을 출력합니다.

    Args:
        logger: 로거 객체
        step: 현재 단계 번호
        total: 전체 단계 수
        message: 단계 설명

    Example:
        >>> print_step(logger, 1, 5, "설정 로드 중...")
        # 출력: [1/5] 설정 로드 중...
    """
    logger.info(f"[{step}/{total}] {message}")


def print_progress(
    logger: logging.Logger,
    current: int,
    total: int,
    prefix: str = "",
    suffix: str = ""
) -> None:
    """
    진행률 바를 출력합니다.

    Args:
        logger: 로거 객체
        current: 현재 진행 수
        total: 전체 수
        prefix: 앞에 붙을 텍스트
        suffix: 뒤에 붙을 텍스트

    Example:
        >>> print_progress(logger, 50, 200, prefix="인덱싱")
        # 출력: 인덱싱: [████████████░░░░░░░░░░░░░░░░░░] 25.0% (50/200)
    """
    if total == 0:
        percent = 100.0
    else:
        percent = (current / total) * 100

    # 진행률 바 생성 (30칸)
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else bar_length
    bar = "█" * filled + "░" * (bar_length - filled)

    # 메시지 구성
    message = f"{prefix}: [{bar}] {percent:.1f}% ({current}/{total})"
    if suffix:
        message += f" {suffix}"

    logger.info(message)


def print_statistics(
    logger: logging.Logger,
    stats: dict,
    title: str = "통계"
) -> None:
    """
    통계 정보를 테이블 형식으로 출력합니다.

    Args:
        logger: 로거 객체
        stats: 통계 딕셔너리 (get_statistics() 결과)
        title: 테이블 제목

    Example:
        >>> stats = {'total': 100, 'pending': 50, 'success': 40, 'failed': 10}
        >>> print_statistics(logger, stats)
        # 출력:
        # ┌─────────────────────────────────┐
        # │         📊 통계                  │
        # ├─────────────────────────────────┤
        # │ 전체 URL    │           100 개  │
        # │ 대기 중     │            50 개  │
        # │ 성공        │            40 개  │
        # │ 실패        │            10 개  │
        # └─────────────────────────────────┘
    """
    logger.info("")
    logger.info(f"┌─────────────────────────────────┐")
    logger.info(f"│         📊 {title:<20} │")
    logger.info(f"├─────────────────────────────────┤")
    logger.info(f"│ 전체 URL    │ {stats.get('total', 0):>10,} 개  │")
    logger.info(f"│ 대기 중     │ {stats.get('pending', 0):>10,} 개  │")
    logger.info(f"│ 성공        │ {stats.get('success', 0):>10,} 개  │")
    logger.info(f"│ 실패        │ {stats.get('failed', 0):>10,} 개  │")
    logger.info(f"└─────────────────────────────────┘")


def print_result_summary(
    logger: logging.Logger,
    success_count: int,
    fail_count: int,
    total_time: float
) -> None:
    """
    실행 결과 요약을 출력합니다.

    Args:
        logger: 로거 객체
        success_count: 성공한 URL 수
        fail_count: 실패한 URL 수
        total_time: 총 소요 시간 (초)

    Example:
        >>> print_result_summary(logger, 180, 20, 125.5)
    """
    total = success_count + fail_count
    success_rate = (success_count / total * 100) if total > 0 else 0

    logger.info("")
    logger.info("═" * 55)
    logger.info("📋 실행 결과 요약")
    logger.info("═" * 55)
    logger.info(f"  • 처리된 URL: {total:,}개")
    logger.info(f"  • 성공: {success_count:,}개 ({success_rate:.1f}%)")
    logger.info(f"  • 실패: {fail_count:,}개")
    logger.info(f"  • 소요 시간: {total_time:.1f}초")
    logger.info("═" * 55)


def print_error(
    logger: logging.Logger,
    message: str,
    error: Optional[Exception] = None
) -> None:
    """
    에러 메시지를 출력합니다.

    Args:
        logger: 로거 객체
        message: 에러 메시지
        error: 예외 객체 (선택)

    Example:
        >>> try:
        ...     raise ValueError("잘못된 값")
        ... except Exception as e:
        ...     print_error(logger, "설정 로드 실패", e)
    """
    logger.error(f"❌ {message}")
    if error:
        logger.error(f"   상세: {str(error)}")
        logger.debug(f"예외 정보:", exc_info=True)


def print_success(logger: logging.Logger, message: str) -> None:
    """
    성공 메시지를 출력합니다.

    Args:
        logger: 로거 객체
        message: 성공 메시지
    """
    logger.info(f"✅ {message}")


def print_warning(logger: logging.Logger, message: str) -> None:
    """
    경고 메시지를 출력합니다.

    Args:
        logger: 로거 객체
        message: 경고 메시지
    """
    logger.warning(f"⚠️  {message}")


def print_info(logger: logging.Logger, message: str) -> None:
    """
    정보 메시지를 출력합니다.

    Args:
        logger: 로거 객체
        message: 정보 메시지
    """
    logger.info(f"ℹ️  {message}")
