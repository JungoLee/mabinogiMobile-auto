# -*- coding: utf-8 -*-
"""
Simple Real-time Monitor
간단한 실시간 화면 모니터링 (OpenCV 창으로 표시)
"""

import pyautogui
import cv2
import numpy as np
import datetime
import os
import sys

# Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create screenshots directory
SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

print("=" * 70)
print("Simple Real-time Monitor")
print("=" * 70)
print()
print("Controls:")
print("  [S] - Save screenshot")
print("  [Q] - Quit")
print()
print("Opening monitor window...")
print("=" * 70)

frame_count = 0
screenshot_count = 0

try:
    while True:
        frame_count += 1

        # 화면 캡처
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 화면 크기 조정 (너무 크면 보기 어려우므로)
        height, width = frame.shape[:2]
        scale = 0.5  # 50% 크기로 축소
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height))

        # 정보 오버레이
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Screenshots: {screenshot_count}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 화면 표시
        cv2.imshow('Monitor (S: Save, Q: Quit)', frame)

        # 키 입력 처리 (30ms 대기)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('s') or key == ord('S'):
            # 스크린샷 저장
            screenshot_count += 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitor_{timestamp}_{screenshot_count}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)

            # 원본 크기로 저장
            original_screenshot = pyautogui.screenshot()
            original_screenshot.save(filepath)

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Screenshot saved: {filename}")

        elif key == ord('q') or key == ord('Q'):
            print("\nQuitting...")
            break

except KeyboardInterrupt:
    print("\nInterrupted by user")

finally:
    cv2.destroyAllWindows()
    print()
    print("=" * 70)
    print(f"Total frames: {frame_count}")
    print(f"Total screenshots: {screenshot_count}")
    print("=" * 70)
