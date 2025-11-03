# -*- coding: utf-8 -*-
"""
Real-time Screen Monitor
실시간으로 화면을 모니터링하고 특정 조건이 발생하면 알림
"""

import pyautogui
import cv2
import numpy as np
import datetime
import os
import sys
import time

# Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class RealtimeMonitor:
    def __init__(self, region=None):
        """
        실시간 모니터 초기화

        Args:
            region: 모니터링할 영역 (x, y, width, height). None이면 전체 화면
        """
        self.region = region
        self.running = False
        self.screenshot_dir = "screenshots"
        self.monitoring_log = []

        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def log(self, message):
        """로그 출력 및 저장"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.monitoring_log.append(log_message)

    def capture_current(self):
        """현재 화면 캡처"""
        if self.region:
            return pyautogui.screenshot(region=self.region)
        return pyautogui.screenshot()

    def save_screenshot(self, prefix="alert"):
        """스크린샷 저장"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        screenshot = self.capture_current()
        screenshot.save(filepath)
        self.log(f"Screenshot saved: {filename}")
        return filepath

    def detect_color_change(self, x, y, target_color, threshold=30):
        """
        특정 좌표의 색상 변화 감지

        Args:
            x, y: 감지할 좌표
            target_color: 찾을 RGB 색상 (r, g, b)
            threshold: 색상 차이 허용 범위
        """
        current_color = pyautogui.pixel(x, y)

        # RGB 차이 계산
        diff = sum(abs(current_color[i] - target_color[i]) for i in range(3))

        if diff <= threshold:
            return True, current_color
        return False, current_color

    def detect_screen_change(self, previous_frame, threshold=0.1):
        """
        화면 전체 변화 감지

        Args:
            previous_frame: 이전 프레임
            threshold: 변화 감지 임계값 (0~1)
        """
        current_frame = self.capture_current()

        # 이미지를 numpy 배열로 변환
        prev_array = np.array(previous_frame)
        curr_array = np.array(current_frame)

        # 차이 계산
        diff = cv2.absdiff(prev_array, curr_array)
        diff_percent = np.sum(diff) / (diff.size * 255)

        if diff_percent > threshold:
            return True, current_frame, diff_percent
        return False, current_frame, diff_percent

    def monitor_pixel_color(self, x, y, target_color, check_interval=1.0):
        """
        특정 픽셀 색상 모니터링

        Args:
            x, y: 모니터링할 좌표
            target_color: 감지할 RGB 색상
            check_interval: 체크 간격(초)
        """
        self.running = True
        self.log("=" * 70)
        self.log(f"Pixel Color Monitor Started")
        self.log(f"Position: ({x}, {y})")
        self.log(f"Target Color: RGB{target_color}")
        self.log(f"Check Interval: {check_interval}s")
        self.log("Press Ctrl+C to stop")
        self.log("=" * 70)

        try:
            while self.running:
                is_match, current_color = self.detect_color_change(x, y, target_color)

                if is_match:
                    self.log(f"[ALERT] Target color detected! RGB{current_color}")
                    self.save_screenshot("color_match")
                else:
                    print(f"\r[MONITOR] Current: RGB{current_color}", end='', flush=True)

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.log("\nMonitoring stopped by user")
        finally:
            self.running = False

    def monitor_screen_change(self, check_interval=1.0, sensitivity=0.05):
        """
        화면 변화 모니터링

        Args:
            check_interval: 체크 간격(초)
            sensitivity: 변화 감지 민감도 (0~1, 낮을수록 민감)
        """
        self.running = True
        self.log("=" * 70)
        self.log(f"Screen Change Monitor Started")
        self.log(f"Region: {'Full Screen' if not self.region else self.region}")
        self.log(f"Check Interval: {check_interval}s")
        self.log(f"Sensitivity: {sensitivity}")
        self.log("Press Ctrl+C to stop")
        self.log("=" * 70)

        # 초기 프레임 캡처
        previous_frame = self.capture_current()
        self.log("Initial frame captured")

        try:
            change_count = 0
            while self.running:
                changed, current_frame, diff_percent = self.detect_screen_change(
                    previous_frame, sensitivity
                )

                if changed:
                    change_count += 1
                    self.log(f"[CHANGE #{change_count}] Screen changed! Difference: {diff_percent:.4f}")
                    self.save_screenshot(f"change_{change_count}")
                else:
                    print(f"\r[MONITOR] Diff: {diff_percent:.6f}", end='', flush=True)

                previous_frame = current_frame
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.log(f"\nMonitoring stopped. Total changes detected: {change_count}")
        finally:
            self.running = False

    def monitor_continuous(self, fps=2):
        """
        연속 화면 모니터링 (실시간 표시)

        Args:
            fps: 초당 프레임 수
        """
        self.running = True
        self.log("=" * 70)
        self.log(f"Continuous Monitor Started")
        self.log(f"FPS: {fps}")
        self.log("Press 'S' to save screenshot, 'Q' to quit")
        self.log("=" * 70)

        interval = 1.0 / fps
        frame_count = 0

        try:
            while self.running:
                frame_count += 1
                screenshot = self.capture_current()

                # OpenCV로 변환하여 표시
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # 정보 오버레이
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Frame: {frame_count}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # 화면 표시
                cv2.imshow('Real-time Monitor (S: Save, Q: Quit)', frame)

                # 키 입력 처리
                key = cv2.waitKey(int(interval * 1000)) & 0xFF
                if key == ord('s') or key == ord('S'):
                    filepath = self.save_screenshot("manual")
                    self.log(f"Manual screenshot saved: {filepath}")
                elif key == ord('q') or key == ord('Q'):
                    self.log("Quit requested")
                    break

        except KeyboardInterrupt:
            self.log("\nMonitoring stopped by user")
        finally:
            cv2.destroyAllWindows()
            self.running = False


def main():
    print("=" * 70)
    print("Real-time Screen Monitor")
    print("=" * 70)
    print()
    print("Select monitoring mode:")
    print("  1. Pixel Color Monitor - 특정 좌표의 색상 변화 감지")
    print("  2. Screen Change Monitor - 화면 전체 변화 감지")
    print("  3. Continuous Monitor - 실시간 화면 표시 (OpenCV 창)")
    print()

    choice = input("Enter mode (1/2/3): ").strip()

    monitor = RealtimeMonitor()

    if choice == "1":
        print("\nPixel Color Monitor")
        x = int(input("Enter X coordinate: "))
        y = int(input("Enter Y coordinate: "))
        r = int(input("Enter target R (0-255): "))
        g = int(input("Enter target G (0-255): "))
        b = int(input("Enter target B (0-255): "))
        interval = float(input("Check interval (seconds, default 1.0): ") or "1.0")

        monitor.monitor_pixel_color(x, y, (r, g, b), interval)

    elif choice == "2":
        print("\nScreen Change Monitor")
        interval = float(input("Check interval (seconds, default 1.0): ") or "1.0")
        sensitivity = float(input("Sensitivity (0.01-0.5, default 0.05): ") or "0.05")

        monitor.monitor_screen_change(interval, sensitivity)

    elif choice == "3":
        print("\nContinuous Monitor")
        fps = int(input("FPS (1-10, default 2): ") or "2")

        monitor.monitor_continuous(fps)

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
