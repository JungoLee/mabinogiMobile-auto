# -*- coding: utf-8 -*-
"""
Centralized Logging Configuration
중앙화된 로깅 설정
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from .constants import LOG_TIME_FORMAT, LOG_DATE_FORMAT


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터 (콘솔용)"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    로거 설정 및 반환

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 파일에 저장 안 함)
        use_colors: 콘솔 출력에 색상 사용 여부

    Returns:
        설정된 Logger 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()

    # 포맷 설정
    log_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
    date_format = LOG_TIME_FORMAT

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_colors and sys.platform == 'win32':
        # Windows ANSI 색상 활성화
        import os
        os.system('color')
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    elif use_colors:
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (옵션)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)

        # 파일에는 색상 코드 제거
        file_formatter = logging.Formatter(log_format, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    기존 로거 반환 (없으면 기본 설정으로 생성)

    Args:
        name: 로거 이름

    Returns:
        Logger 객체
    """
    logger = logging.getLogger(name)

    # 핸들러가 없으면 기본 설정
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


# 기본 로거 인스턴스
default_logger = setup_logger('automation', level=logging.INFO)
