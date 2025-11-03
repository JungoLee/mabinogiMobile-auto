# -*- coding: utf-8 -*-
"""
Core Monitor Module
화면 모니터링 핵심 기능
"""

import pyautogui
import cv2
import numpy as np
import datetime
import os
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Monitor:
    """화면 모니터링 코어 클래스"""

    def __init__(self, region=None, screenshot_dir="screenshots"):
        """
        Args:
            region: 모니터링할 영역 (x, y, width, height). None이면 전체 화면
            screenshot_dir: 스크린샷 저장 디렉토리
        """
        self.region = region
        self.screenshot_dir = screenshot_dir
        self.running = False
        self.log_enabled = True

        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

    def log(self, message):
        """로그 출력"""
        if self.log_enabled:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def capture(self):
        """현재 화면 캡처"""
        if self.region:
            return pyautogui.screenshot(region=self.region)
        return pyautogui.screenshot()

    def save_screenshot(self, prefix="screenshot"):
        """스크린샷 저장"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        screenshot = self.capture()
        screenshot.save(filepath)
        self.log(f"Screenshot saved: {filename}")
        return filepath

    def get_pixel_color(self, x, y):
        """특정 좌표의 픽셀 색상 가져오기"""
        return pyautogui.pixel(x, y)

    def check_color_match(self, x, y, target_color, threshold=30):
        """
        특정 좌표의 색상이 목표 색상과 일치하는지 확인

        Args:
            x, y: 확인할 좌표
            target_color: 목표 RGB 색상 (r, g, b)
            threshold: 허용 오차

        Returns:
            bool: 일치 여부
        """
        current_color = self.get_pixel_color(x, y)
        diff = sum(abs(current_color[i] - target_color[i]) for i in range(3))
        return diff <= threshold

    def find_image_on_screen(self, template_path, confidence=0.8):
        """
        화면에서 특정 이미지 찾기

        Args:
            template_path: 찾을 이미지 파일 경로
            confidence: 일치도 (0~1)

        Returns:
            tuple: (x, y, width, height) 또는 None
        """
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                return location
        except Exception as e:
            self.log(f"Image search error: {str(e)}")
        return None

    def wait_for_image(self, template_path, timeout=10, check_interval=0.5):
        """
        이미지가 나타날 때까지 대기

        Args:
            template_path: 찾을 이미지
            timeout: 최대 대기 시간(초)
            check_interval: 확인 간격(초)

        Returns:
            tuple: (x, y, width, height) 또는 None
        """
        self.log(f"Waiting for image: {template_path}")
        start_time = time.time()

        while time.time() - start_time < timeout:
            location = self.find_image_on_screen(template_path)
            if location:
                self.log(f"Image found at {location}")
                return location
            time.sleep(check_interval)

        self.log("Image not found (timeout)")
        return None

    def wait_for_color(self, x, y, target_color, timeout=10, check_interval=0.5, threshold=30):
        """
        특정 색상이 나타날 때까지 대기

        Args:
            x, y: 확인할 좌표
            target_color: 목표 색상 (r, g, b)
            timeout: 최대 대기 시간(초)
            check_interval: 확인 간격(초)
            threshold: 허용 오차

        Returns:
            bool: 색상 발견 여부
        """
        self.log(f"Waiting for color RGB{target_color} at ({x}, {y})")
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.check_color_match(x, y, target_color, threshold):
                self.log(f"Color matched!")
                return True
            time.sleep(check_interval)

        self.log("Color not matched (timeout)")
        return False

    def detect_screen_change(self, previous_image, threshold=0.05):
        """
        화면 변화 감지

        Args:
            previous_image: 이전 화면 이미지
            threshold: 변화 감지 임계값 (0~1)

        Returns:
            tuple: (변화여부, 현재이미지, 변화율)
        """
        current_image = self.capture()

        prev_array = np.array(previous_image)
        curr_array = np.array(current_image)

        diff = cv2.absdiff(prev_array, curr_array)
        diff_percent = np.sum(diff) / (diff.size * 255)

        changed = diff_percent > threshold
        return changed, current_image, diff_percent
