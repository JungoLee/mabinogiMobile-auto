# -*- coding: utf-8 -*-
"""
Image Detection Module
이미지 감지 및 템플릿 매칭 모듈
"""

from typing import Optional, Tuple, List
import cv2
import numpy as np
import pyautogui
from PIL import Image

from .constants import (
    IMAGE_CONFIDENCE_THRESHOLD,
    TEMPLATE_MATCH_THRESHOLD,
    DUPLICATE_DETECTION_THRESHOLD_RATIO
)
from .exceptions import TemplateLoadError


class ImageDetector:
    """이미지 감지 및 템플릿 매칭 클래스"""

    @staticmethod
    def load_template(template_path: str) -> np.ndarray:
        """
        템플릿 이미지 로드

        Args:
            template_path: 템플릿 이미지 경로

        Returns:
            OpenCV 이미지 (numpy array)

        Raises:
            TemplateLoadError: 템플릿 로드 실패 시
        """
        template = cv2.imread(template_path)
        if template is None:
            raise TemplateLoadError(template_path)
        return template

    @staticmethod
    def capture_screen(area: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        화면 캡처

        Args:
            area: 캡처 영역 (x1, y1, x2, y2), None이면 전체 화면

        Returns:
            OpenCV 형식의 이미지 (BGR)
        """
        screenshot = pyautogui.screenshot()

        if area:
            x1, y1, x2, y2 = area
            screenshot = screenshot.crop((x1, y1, x2, y2))

        # PIL Image to OpenCV (BGR)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    @staticmethod
    def find_template(
        screen: np.ndarray,
        template: np.ndarray,
        confidence: float = IMAGE_CONFIDENCE_THRESHOLD
    ) -> Optional[Tuple[int, int, float]]:
        """
        화면에서 템플릿 찾기

        Args:
            screen: 화면 이미지 (OpenCV 형식)
            template: 템플릿 이미지 (OpenCV 형식)
            confidence: 최소 신뢰도 (0.0 ~ 1.0)

        Returns:
            (x, y, confidence) 중심 좌표와 신뢰도, 없으면 None
        """
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)

        return None

    @staticmethod
    def find_all_templates(
        screen: np.ndarray,
        template: np.ndarray,
        threshold: float = TEMPLATE_MATCH_THRESHOLD
    ) -> List[Tuple[int, int, float]]:
        """
        화면에서 모든 템플릿 매칭 위치 찾기

        Args:
            screen: 화면 이미지
            template: 템플릿 이미지
            threshold: 최소 신뢰도

        Returns:
            [(x, y, confidence), ...] 중심 좌표와 신뢰도 리스트
        """
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        h, w = template.shape[:2]
        matches = []

        for pt in zip(*locations[::-1]):
            x, y = pt
            confidence = result[y, x]
            center_x = x + w // 2
            center_y = y + h // 2
            matches.append((center_x, center_y, confidence))

        return matches

    @staticmethod
    def remove_duplicates(
        matches: List[Tuple[int, int, float]],
        distance_threshold: int = None
    ) -> List[Tuple[int, int, float]]:
        """
        중복된 매칭 결과 제거 (가까운 위치는 하나로)

        Args:
            matches: [(x, y, confidence), ...] 매칭 결과
            distance_threshold: 중복으로 간주할 거리 (픽셀), None이면 자동 계산

        Returns:
            중복 제거된 매칭 결과
        """
        if not matches:
            return []

        # 신뢰도 기준 내림차순 정렬
        sorted_matches = sorted(matches, key=lambda m: m[2], reverse=True)

        filtered = []
        for x, y, conf in sorted_matches:
            is_duplicate = False

            for fx, fy, _ in filtered:
                distance = np.sqrt((x - fx) ** 2 + (y - fy) ** 2)

                if distance_threshold is None:
                    # 자동 임계값: 첫 번째 매칭의 신뢰도 기반
                    threshold = 50  # 기본값
                else:
                    threshold = distance_threshold

                if distance < threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append((x, y, conf))

        return filtered

    def find_image_in_area(
        self,
        template_path: str,
        area: Optional[Tuple[int, int, int, int]] = None,
        confidence: float = IMAGE_CONFIDENCE_THRESHOLD
    ) -> Optional[Tuple[int, int]]:
        """
        영역 내에서 이미지 찾기 (편의 메서드)

        Args:
            template_path: 템플릿 이미지 경로
            area: 검색 영역 (x1, y1, x2, y2)
            confidence: 최소 신뢰도

        Returns:
            (x, y) 절대 좌표, 없으면 None
        """
        try:
            template = self.load_template(template_path)
            screen = self.capture_screen(area)

            result = self.find_template(screen, template, confidence)

            if result:
                x, y, conf = result

                # 상대 좌표 -> 절대 좌표 변환
                if area:
                    x += area[0]
                    y += area[1]

                return (x, y)

            return None

        except Exception:
            return None
