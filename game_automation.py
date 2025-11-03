"""
게임 자동화 스크립트
화면을 캡처하고 특정 텍스트를 인식하여 자동으로 동작을 수행합니다.
"""

import pyautogui
import pytesseract
from PIL import Image
import time
import sys
import datetime
import cv2
import numpy as np

# 설정
pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동하면 중단
pyautogui.PAUSE = 0.5  # 각 동작 사이 0.5초 대기

# Tesseract 경로 설정 (Windows 기준)
# 설치 후 경로를 본인 환경에 맞게 수정하세요
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class GameAutomation:
    def __init__(self):
        """게임 자동화 클래스 초기화"""
        self.running = False
        self.log_enabled = True

    def log(self, message):
        """로그 출력"""
        if self.log_enabled:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")

    def capture_screen(self, region=None):
        """
        화면 캡처

        Args:
            region: 캡처할 영역 (x, y, width, height). None이면 전체 화면

        Returns:
            PIL Image 객체
        """
        if region:
            screenshot = pyautogui.screenshot(region=region)
            self.log(f"화면 캡처 완료 (영역: {region})")
        else:
            screenshot = pyautogui.screenshot()
            self.log("전체 화면 캡처 완료")
        return screenshot

    def extract_text(self, image, lang='kor+eng'):
        """
        이미지에서 텍스트 추출

        Args:
            image: PIL Image 객체
            lang: 인식할 언어 ('kor+eng', 'eng', 'kor' 등)

        Returns:
            인식된 텍스트 문자열
        """
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()

    def find_text_in_region(self, text_to_find, region=None, lang='kor+eng'):
        """
        특정 영역에서 텍스트 찾기

        Args:
            text_to_find: 찾을 텍스트
            region: 검색할 영역
            lang: 인식할 언어

        Returns:
            텍스트가 발견되면 True, 아니면 False
        """
        screenshot = self.capture_screen(region)
        extracted_text = self.extract_text(screenshot, lang)

        if text_to_find in extracted_text:
            self.log(f"✓ 텍스트 발견: '{text_to_find}'")
            return True
        return False

    def click_at(self, x, y, clicks=1, button='left', delay=0):
        """
        특정 좌표 클릭

        Args:
            x, y: 클릭할 좌표
            clicks: 클릭 횟수 (1=일반, 2=더블클릭)
            button: 'left', 'right', 'middle'
            delay: 클릭 후 대기 시간
        """
        pyautogui.click(x, y, clicks=clicks, button=button)
        self.log(f"클릭: ({x}, {y}), 버튼: {button}, 횟수: {clicks}")
        if delay > 0:
            time.sleep(delay)

    def press_key(self, key, delay=0):
        """
        키보드 키 입력

        Args:
            key: 누를 키 ('enter', 'space', 'esc' 등)
            delay: 입력 후 대기 시간
        """
        pyautogui.press(key)
        self.log(f"키 입력: {key}")
        if delay > 0:
            time.sleep(delay)

    def press_hotkey(self, *keys, delay=0):
        """
        조합키 입력

        Args:
            keys: 조합할 키들 ('ctrl', 'c' 등)
            delay: 입력 후 대기 시간
        """
        pyautogui.hotkey(*keys)
        self.log(f"조합키 입력: {'+'.join(keys)}")
        if delay > 0:
            time.sleep(delay)

    def type_text(self, text, interval=0.1):
        """
        텍스트 입력

        Args:
            text: 입력할 텍스트
            interval: 각 글자 사이 간격
        """
        pyautogui.write(text, interval=interval)
        self.log(f"텍스트 입력: {text}")

    def find_image(self, template_path, threshold=0.8, region=None):
        """
        화면에서 특정 이미지 찾기

        Args:
            template_path: 찾을 이미지 파일 경로
            threshold: 일치 임계값 (0~1, 높을수록 정확)
            region: 검색할 영역

        Returns:
            찾으면 (x, y, width, height), 못 찾으면 None
        """
        screenshot = self.capture_screen(region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)

        if template is None:
            self.log(f"❌ 템플릿 이미지를 불러올 수 없음: {template_path}")
            return None

        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape[:2]
            self.log(f"✓ 이미지 발견: {template_path} (신뢰도: {max_val:.2f})")
            return (max_loc[0], max_loc[1], w, h)

        return None

    def run_automation(self, check_interval=2):
        """
        자동화 실행 (예제)

        Args:
            check_interval: 각 체크 사이 대기 시간 (초)
        """
        self.running = True
        self.log("===== 게임 자동화 시작 =====")
        self.log("종료하려면 마우스를 화면 왼쪽 위 모서리로 이동하세요")

        try:
            while self.running:
                # 예제 1: 특정 텍스트 찾아서 클릭
                if self.find_text_in_region("시작", region=(100, 100, 400, 300)):
                    self.click_at(250, 200, delay=1)
                    self.log("'시작' 버튼 클릭 완료")

                # 예제 2: 다른 텍스트 찾아서 키 입력
                elif self.find_text_in_region("확인"):
                    self.press_key('enter', delay=1)
                    self.log("'확인' 발견 후 Enter 입력")

                # 예제 3: 여러 조건 체크
                screenshot = self.capture_screen()
                text = self.extract_text(screenshot)

                if "준비완료" in text:
                    self.click_at(500, 300)
                    self.press_key('space', delay=1)
                    self.log("게임 준비 완료 처리")

                elif "게임시작" in text:
                    self.press_hotkey('ctrl', 'enter', delay=1)
                    self.log("게임 시작 처리")

                # 다음 체크까지 대기
                time.sleep(check_interval)

        except pyautogui.FailSafeException:
            self.log("===== 사용자에 의해 중단됨 =====")
        except KeyboardInterrupt:
            self.log("===== Ctrl+C로 중단됨 =====")
        except Exception as e:
            self.log(f"❌ 오류 발생: {str(e)}")
        finally:
            self.running = False
            self.log("===== 게임 자동화 종료 =====")


def main():
    """메인 함수"""
    print("=" * 50)
    print("게임 자동화 스크립트")
    print("=" * 50)
    print()
    print("주의사항:")
    print("1. Tesseract OCR이 설치되어 있어야 합니다")
    print("2. game_automation.py 파일에서 Tesseract 경로를 확인하세요")
    print("3. 마우스를 화면 왼쪽 위로 이동하면 중단됩니다")
    print()

    # 자동화 시작 전 대기
    print("3초 후 자동화를 시작합니다...")
    time.sleep(3)

    # 자동화 실행
    automation = GameAutomation()
    automation.run_automation(check_interval=2)


if __name__ == "__main__":
    main()
