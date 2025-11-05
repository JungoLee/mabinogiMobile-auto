# -*- coding: utf-8 -*-
"""
Daily Scenario Story
매일 시나리오 - 캐릭터 선택 및 게임 시작
"""

from typing import Optional, List, Tuple

from core.story_base import StoryBase
from core.image_detector import ImageDetector
from core.ocr_processor import OCRProcessor
from core.constants import IMAGE_CONFIDENCE_THRESHOLD


class DailyScenarioStory(StoryBase):
    """매일 시나리오 자동화 스토리"""

    def __init__(self):
        super().__init__("Daily Scenario")
        self.detection_area: Optional[Tuple[int, int, int, int]] = None
        self.image_detector = ImageDetector()
        self.ocr_processor = OCRProcessor()

        # 이미지 템플릿 경로
        self.template_game_start = "assets/images/UI/game_start.png"
        self.template_game_start_yellow = "assets/images/UI/game_start_yellow.png"
        self.template_currency_example = "assets/images/system/character_choice_coins.png"

    def set_detection_area(self, area: Tuple[int, int, int, int]) -> None:
        """감지 영역 설정 (x1, y1, x2, y2)"""
        self.detection_area = area
        self.log(f"Detection area set: {area}")

    def find_image_in_area(
        self,
        template_path: str,
        confidence: float = IMAGE_CONFIDENCE_THRESHOLD
    ) -> Optional[Tuple[int, int]]:
        """
        감지 영역 내에서 이미지 찾기

        Args:
            template_path: 템플릿 이미지 경로
            confidence: 최소 신뢰도

        Returns:
            (x, y) 중심 좌표 또는 None
        """
        try:
            result = self.image_detector.find_image_in_area(
                template_path,
                area=self.detection_area,
                confidence=confidence
            )

            if result:
                x, y = result
                self.log(f"✓ Image found at ({x}, {y})")
                return result
            else:
                self.log(f"✗ Image not found: {template_path}")
                return None

        except Exception as e:
            self.log(f"❌ Error finding image: {e}")
            return None

    def find_all_currency_positions(self) -> List[Tuple[int, int, int]]:
        """
        모든 캐릭터의 은동전(왼쪽 숫자) 위치와 값을 찾기

        Returns:
            [(value, x, y), ...] 리스트
        """
        try:
            # 화면 캡처
            screen = self.image_detector.capture_screen(area=self.detection_area)

            # 템플릿 로드
            template = self.image_detector.load_template(self.template_currency_example)

            # OCR 프로세서로 재화 찾기
            currency_list = self.ocr_processor.find_currency_values(screen, template)

            # 절대 좌표로 변환
            if self.detection_area:
                offset_x, offset_y = self.detection_area[0], self.detection_area[1]
                currency_list = [
                    (value, x + offset_x, y + offset_y)
                    for value, x, y in currency_list
                ]

            # 로그 출력
            for value, x, y in currency_list:
                self.log(f"  Found currency: {value} at ({x}, {y})")

            return currency_list

        except Exception as e:
            self.log(f"❌ Error finding currencies: {e}")
            return []

    def click_at(self, x: int, y: int, delay: float = 0.5) -> bool:
        """
        좌표 클릭 (automation 모듈 사용)

        Args:
            x: X 좌표
            y: Y 좌표
            delay: 클릭 후 대기 시간

        Returns:
            성공 여부
        """
        try:
            self.log(f"Clicking at ({x}, {y})")
            self.automation.click(x, y, delay=delay)
            return True
        except Exception as e:
            self.log(f"❌ Click error: {e}")
            return False

    def start(self) -> bool:
        """스토리 실행"""
        try:
            self.log("=" * 60)
            self.log("Starting Daily Scenario Story")
            self.log("=" * 60)

            # Step 1: game_start 버튼 찾기 및 클릭
            self.log("\n[Step 1] Finding 'game_start' button...")
            game_start_pos = self.find_image_in_area(self.template_game_start, confidence=0.8)

            if not game_start_pos:
                self.log("❌ 'game_start' button not found")
                return False

            self.log("Waiting 3 seconds before click...")
            self.smart_sleep(3)

            if not self.click_at(game_start_pos[0], game_start_pos[1]):
                return False

            self.log("✓ 'game_start' button clicked")

            # Step 2: 캐릭터 선택 (은동전이 가장 많은 캐릭터)
            self.log("\n[Step 2] Finding character with highest currency...")
            self.smart_sleep(2)  # 화면 로딩 대기

            currency_list = self.find_all_currency_positions()

            if not currency_list:
                self.log("⚠ No currency found, trying alternative method...")
                # 대체 방법: 화면 중앙의 첫 번째 캐릭터 선택
                if self.detection_area:
                    x1, y1, x2, y2 = self.detection_area
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    self.click_at(center_x, center_y)
            else:
                # 은동전이 가장 많은 캐릭터 선택
                currency_list.sort(reverse=True)  # 내림차순 정렬
                max_currency, click_x, click_y = currency_list[0]

                self.log(f"✓ Highest currency: {max_currency}")
                self.click_at(click_x, click_y)

            self.log("Waiting 2 seconds after character selection...")
            self.smart_sleep(2)

            # Step 3: game_start_yellow 버튼 찾기 및 클릭
            self.log("\n[Step 3] Finding 'game_start_yellow' button...")
            game_start_yellow_pos = self.find_image_in_area(self.template_game_start_yellow, confidence=0.8)

            if not game_start_yellow_pos:
                self.log("❌ 'game_start_yellow' button not found")
                return False

            if not self.click_at(game_start_yellow_pos[0], game_start_yellow_pos[1]):
                return False

            self.log("✓ 'game_start_yellow' button clicked")

            self.log("\n" + "=" * 60)
            self.log("✓ Daily Scenario Story Completed")
            self.log("=" * 60)

            return True

        except Exception as e:
            self.log(f"❌ Story execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
