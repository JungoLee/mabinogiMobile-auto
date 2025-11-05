# -*- coding: utf-8 -*-
"""
OCR Processing Module
OCR (광학 문자 인식) 처리 모듈
"""

from typing import Optional, List, Tuple
import cv2
import numpy as np
import pytesseract

from .constants import OCR_CONFIG_DIGITS, OCR_LANGUAGE


class OCRProcessor:
    """OCR 처리 클래스"""

    @staticmethod
    def preprocess_for_digits(image: np.ndarray) -> np.ndarray:
        """
        숫자 인식을 위한 이미지 전처리

        Args:
            image: 입력 이미지 (OpenCV 형식)

        Returns:
            전처리된 이미지 (이진화)
        """
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Otsu 이진화
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    @staticmethod
    def extract_digits(image: np.ndarray, config: str = OCR_CONFIG_DIGITS) -> Optional[int]:
        """
        이미지에서 숫자 추출

        Args:
            image: 입력 이미지
            config: Tesseract 설정

        Returns:
            추출된 숫자, 실패 시 None
        """
        try:
            # 전처리
            preprocessed = OCRProcessor.preprocess_for_digits(image)

            # OCR 수행
            text = pytesseract.image_to_string(preprocessed, config=config)

            # 숫자만 추출
            digits = ''.join(filter(str.isdigit, text))

            if digits:
                return int(digits)

            return None

        except Exception:
            return None

    @staticmethod
    def extract_text(
        image: np.ndarray,
        language: str = OCR_LANGUAGE,
        config: str = ''
    ) -> str:
        """
        이미지에서 텍스트 추출

        Args:
            image: 입력 이미지
            language: OCR 언어 (기본: 영어)
            config: Tesseract 설정

        Returns:
            추출된 텍스트
        """
        try:
            text = pytesseract.image_to_string(image, lang=language, config=config)
            return text.strip()
        except Exception:
            return ""

    @staticmethod
    def find_currency_values(
        screen: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.7
    ) -> List[Tuple[int, int, int]]:
        """
        화면에서 재화(currency) 값과 위치 찾기

        Args:
            screen: 화면 이미지
            template: 재화 아이콘 템플릿
            threshold: 템플릿 매칭 임계값

        Returns:
            [(value, x, y), ...] 재화 값과 중심 좌표 리스트
        """
        # 템플릿 매칭
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        h, w = template.shape[:2]
        currency_list = []

        for pt in zip(*locations[::-1]):
            x, y = pt

            # 중복 제거
            is_duplicate = False
            for _, cx, cy in currency_list:
                if abs(cx - x) < w // 2 and abs(cy - y) < h // 2:
                    is_duplicate = True
                    break

            if not is_duplicate:
                # 왼쪽 절반에서 숫자 읽기 (은동전)
                roi = screen[y:y+h, x:x+w//2]

                # OCR로 숫자 추출
                value = OCRProcessor.extract_digits(roi)

                if value is not None:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    currency_list.append((value, center_x, center_y))

        return currency_list
