# -*- coding: utf-8 -*-
"""
Auto Barrier Check
"결계체크" 텍스트를 발견하면 자동으로 "불결한 소환의 결계" 체크박스 클릭
"""

import pyautogui
import datetime
import os
import sys
import time

# Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import keyboard
except ImportError:
    print("ERROR: keyboard module not installed!")
    print("Install with: pip install keyboard")
    sys.exit(1)

# Create screenshots directory
SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

print("=" * 70)
print("Auto Barrier Check - Manual Mode")
print("=" * 70)
print()
print("How to use:")
print("1. First, find the checkbox coordinates using find_coordinates.py")
print("2. Update CHECKBOX_X and CHECKBOX_Y in this script")
print("3. Press SPACE when you see '결계체크' text")
print("4. Script will click the checkbox automatically")
print()
print("=" * 70)
print()

# 설정값 - 실제 좌표로 수정 필요!
CHECKBOX_X = 500  # 체크박스 X 좌표
CHECKBOX_Y = 300  # 체크박스 Y 좌표

print(f"Current checkbox position: ({CHECKBOX_X}, {CHECKBOX_Y})")
print()
print("To find the correct coordinates:")
print("1. Run: python find_coordinates.py")
print("2. Move mouse to checkbox and press SPACE")
print("3. Update the coordinates in this script")
print()
print("=" * 70)
print()
print("Controls:")
print("  [SPACE] - Click checkbox (when you see '결계체크')")
print("  [T]     - Test click at current position")
print("  [Q]     - Quit")
print()
print("Ready! Waiting for input...")
print("=" * 70)
print()

click_count = 0
test_click_count = 0

try:
    while True:
        if keyboard.is_pressed('space'):
            click_count += 1
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # 클릭 전 스크린샷
            screenshot = pyautogui.screenshot()
            filename = f"before_click_{click_count}_{timestamp.replace(':', '')}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            screenshot.save(filepath)

            print(f"[{timestamp}] Click #{click_count} - Clicking checkbox at ({CHECKBOX_X}, {CHECKBOX_Y})")

            # 체크박스 클릭
            pyautogui.click(CHECKBOX_X, CHECKBOX_Y)

            time.sleep(0.5)

            # 클릭 후 스크린샷
            screenshot = pyautogui.screenshot()
            filename = f"after_click_{click_count}_{timestamp.replace(':', '')}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            screenshot.save(filepath)

            print(f"           Screenshots saved!")
            print()

            time.sleep(0.5)  # Debounce

        elif keyboard.is_pressed('t'):
            test_click_count += 1
            x, y = pyautogui.position()
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Test click #{test_click_count} at current mouse position: ({x}, {y})")
            pyautogui.click(x, y)

            time.sleep(0.5)  # Debounce

        elif keyboard.is_pressed('q'):
            print("\nQuitting...")
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nInterrupted by user")

print()
print("=" * 70)
print(f"Total checkbox clicks: {click_count}")
print(f"Total test clicks: {test_click_count}")
print("=" * 70)
