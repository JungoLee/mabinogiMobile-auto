# -*- coding: utf-8 -*-
"""
Core Automation Module
마우스/키보드 조작 핵심 기능
"""

import pyautogui
import time
import datetime
import sys

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Automation:
    """자동화 조작 코어 클래스"""

    def __init__(self, pause_time=0.5, failsafe=True):
        """
        Args:
            pause_time: 각 동작 후 대기 시간
            failsafe: 안전 모드 (마우스를 모서리로 이동하면 중단)
        """
        pyautogui.PAUSE = pause_time
        pyautogui.FAILSAFE = failsafe
        self.log_enabled = True

    def log(self, message):
        """로그 출력"""
        if self.log_enabled:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def click(self, x, y, clicks=1, button='left', delay=0):
        """
        마우스 클릭

        Args:
            x, y: 클릭할 좌표
            clicks: 클릭 횟수
            button: 'left', 'right', 'middle'
            delay: 클릭 후 대기 시간
        """
        pyautogui.click(x, y, clicks=clicks, button=button)
        self.log(f"Click at ({x}, {y}) - button: {button}, clicks: {clicks}")
        if delay > 0:
            time.sleep(delay)

    def double_click(self, x, y, delay=0):
        """더블 클릭"""
        self.click(x, y, clicks=2, delay=delay)

    def right_click(self, x, y, delay=0):
        """우클릭"""
        self.click(x, y, button='right', delay=delay)

    def move_to(self, x, y, duration=0.5, delay=0):
        """
        마우스 이동

        Args:
            x, y: 이동할 좌표
            duration: 이동 시간
            delay: 이동 후 대기 시간
        """
        pyautogui.moveTo(x, y, duration=duration)
        self.log(f"Move to ({x}, {y})")
        if delay > 0:
            time.sleep(delay)

    def drag_to(self, x, y, duration=0.5, delay=0):
        """
        드래그

        Args:
            x, y: 드래그할 좌표
            duration: 드래그 시간
            delay: 드래그 후 대기 시간
        """
        pyautogui.dragTo(x, y, duration=duration)
        self.log(f"Drag to ({x}, {y})")
        if delay > 0:
            time.sleep(delay)

    def press_key(self, key, delay=0):
        """
        키 입력

        Args:
            key: 누를 키 ('enter', 'space', 'esc', 'a', '1' 등)
            delay: 입력 후 대기 시간
        """
        pyautogui.press(key)
        self.log(f"Press key: {key}")
        if delay > 0:
            time.sleep(delay)

    def hotkey(self, *keys, delay=0):
        """
        조합키 입력

        Args:
            keys: 조합할 키들 ('ctrl', 'c' 등)
            delay: 입력 후 대기 시간
        """
        pyautogui.hotkey(*keys)
        self.log(f"Hotkey: {'+'.join(keys)}")
        if delay > 0:
            time.sleep(delay)

    def type_text(self, text, interval=0.1):
        """
        텍스트 입력

        Args:
            text: 입력할 텍스트
            interval: 각 글자 간격
        """
        pyautogui.write(text, interval=interval)
        self.log(f"Type text: {text}")

    def scroll(self, amount, delay=0):
        """
        마우스 스크롤

        Args:
            amount: 스크롤 양 (양수: 위로, 음수: 아래로)
            delay: 스크롤 후 대기 시간
        """
        pyautogui.scroll(amount)
        self.log(f"Scroll: {amount}")
        if delay > 0:
            time.sleep(delay)

    def wait(self, seconds):
        """대기"""
        self.log(f"Waiting {seconds} seconds...")
        time.sleep(seconds)

    def click_image(self, image_location, delay=0):
        """
        이미지 위치 클릭

        Args:
            image_location: (x, y, width, height) 튜플
            delay: 클릭 후 대기 시간
        """
        if image_location:
            x, y, w, h = image_location
            center_x = x + w // 2
            center_y = y + h // 2
            self.click(center_x, center_y, delay=delay)
        else:
            self.log("No image location provided")
