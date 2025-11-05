# -*- coding: utf-8 -*-
"""
Daily Scenario Story
매일 시나리오 - 캐릭터 선택 및 게임 시작
"""

import time
import pyautogui
import cv2
import numpy as np
import pytesseract
from core.story_base import StoryBase


class DailyScenarioStory(StoryBase):
    """매일 시나리오 자동화 스토리"""

    def __init__(self):
        super().__init__("Daily Scenario")
        self.detection_area = None  # Main에서 전달받을 감지 영역

        # 이미지 템플릿 경로
        self.template_game_start = "assets/images/UI/game_start.png"
        self.template_game_start_yellow = "assets/images/UI/game_start_yellow.png"
        self.template_currency_example = "assets/images/system/character_choice_coins.png"

    def set_detection_area(self, area):
        """감지 영역 설정 (x1, y1, x2, y2)"""
        self.detection_area = area
        self.log(f"Detection area set: {area}")

    def find_image_in_area(self, template_path, confidence=0.8):
        """
        감지 영역 내에서 이미지 찾기

        Returns:
            (x, y) 중심 좌표 또는 None
        """
        try:
            # 전체 화면 캡처
            screenshot = pyautogui.screenshot()

            # 감지 영역으로 제한
            if self.detection_area:
                x1, y1, x2, y2 = self.detection_area
                screenshot = screenshot.crop((x1, y1, x2, y2))
                offset_x, offset_y = x1, y1
            else:
                offset_x, offset_y = 0, 0

            # OpenCV 형식 변환
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template = cv2.imread(template_path)

            if template is None:
                self.log(f"⚠ Template not found: {template_path}")
                return None

            # 템플릿 매칭
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2 + offset_x
                center_y = max_loc[1] + h // 2 + offset_y

                self.log(f"✓ Image found at ({center_x}, {center_y}), confidence: {max_val:.2f}")
                return (center_x, center_y)
            else:
                self.log(f"✗ Image not found (best match: {max_val:.2f})")
                return None

        except Exception as e:
            self.log(f"❌ Error finding image: {e}")
            return None

    def find_all_currency_positions(self):
        """
        모든 캐릭터의 은동전(왼쪽 숫자) 위치와 값을 찾기

        Returns:
            [(value, x, y), ...] 리스트
        """
        try:
            # 전체 화면 캡처
            screenshot = pyautogui.screenshot()

            # 감지 영역으로 제한
            if self.detection_area:
                x1, y1, x2, y2 = self.detection_area
                screenshot = screenshot.crop((x1, y1, x2, y2))
                offset_x, offset_y = x1, y1
            else:
                offset_x, offset_y = 0, 0

            # OpenCV 형식 변환
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 재화 예제 템플릿 로드
            template = cv2.imread(self.template_currency_example)
            if template is None:
                self.log(f"⚠ Currency template not found: {self.template_currency_example}")
                return []

            # 템플릿 매칭 (모든 위치 찾기)
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            locations = np.where(result >= threshold)

            currency_list = []
            h, w = template.shape[:2]

            for pt in zip(*locations[::-1]):
                x, y = pt

                # 중복 제거 (가까운 위치는 하나로)
                is_duplicate = False
                for _, cx, cy in currency_list:
                    if abs(cx - x) < w // 2 and abs(cy - y) < h // 2:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    # OCR로 왼쪽 숫자 읽기 (은동전)
                    roi = screen[y:y+h, x:x+w//2]  # 왼쪽 절반만

                    # OCR 전처리
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    # 숫자 인식
                    text = pytesseract.image_to_string(binary, config='--psm 7 digits')
                    text = ''.join(filter(str.isdigit, text))  # 숫자만 추출

                    if text:
                        value = int(text)
                        center_x = x + w // 2 + offset_x
                        center_y = y + h // 2 + offset_y
                        currency_list.append((value, center_x, center_y))
                        self.log(f"  Found currency: {value} at ({center_x}, {center_y})")

            return currency_list

        except Exception as e:
            self.log(f"❌ Error finding currencies: {e}")
            return []

    def click_at(self, x, y, delay=0.5):
        """좌표 클릭"""
        try:
            self.log(f"Clicking at ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(delay)
            return True
        except Exception as e:
            self.log(f"❌ Click error: {e}")
            return False

    def start(self):
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
            time.sleep(3)

            if not self.click_at(game_start_pos[0], game_start_pos[1]):
                return False

            self.log("✓ 'game_start' button clicked")

            # Step 2: 캐릭터 선택 (은동전이 가장 많은 캐릭터)
            self.log("\n[Step 2] Finding character with highest currency...")
            time.sleep(2)  # 화면 로딩 대기

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
            time.sleep(2)

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
