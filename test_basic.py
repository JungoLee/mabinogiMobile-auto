# -*- coding: utf-8 -*-
"""
Basic Function Test Script (No Tesseract Required)
Mouse position tracking and basic pyautogui features test
"""

import pyautogui
import time
import sys

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Game Automation Basic Test")
print("=" * 60)
print()

# 1. Screen size check
screen_width, screen_height = pyautogui.size()
print(f"[OK] Screen size: {screen_width} x {screen_height}")
print()

# 2. Current mouse position
x, y = pyautogui.position()
print(f"[OK] Current mouse position: ({x}, {y})")
print()

# 3. Screenshot test
print("[OK] Screenshot test...")
screenshot = pyautogui.screenshot()
print(f"     Captured: {screenshot.size[0]} x {screenshot.size[1]}")
print()

# 4. Region screenshot test
print("[OK] Region screenshot test...")
region_screenshot = pyautogui.screenshot(region=(100, 100, 200, 200))
print(f"     Region captured: {region_screenshot.size[0]} x {region_screenshot.size[1]}")
print()

# 5. Pixel color check
pixel_color = pyautogui.pixel(x, y)
print(f"[OK] Pixel color at mouse position: RGB{pixel_color}")
print()

# 6. Mouse position tracking for 5 seconds
print("[OK] Tracking mouse position for 5 seconds...")
print("     (Move your mouse!)")
print()

for i in range(5):
    x, y = pyautogui.position()
    pixel = pyautogui.pixel(x, y)
    print(f"     [{i+1}s] Position: ({x:4d}, {y:4d}) | RGB{pixel}")
    time.sleep(1)

print()
print("=" * 60)
print("All basic tests completed!")
print("=" * 60)
print()
print("Next steps:")
print("1. Install Tesseract OCR (for text recognition)")
print("   https://github.com/UB-Mannheim/tesseract/wiki")
print("2. Run find_coordinates.py to find game coordinates")
print("3. Modify game_automation.py and start automation")
