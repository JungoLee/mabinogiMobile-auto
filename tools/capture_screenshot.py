# -*- coding: utf-8 -*-
"""
Screenshot Capture Tool
Press 'S' to capture screenshot, 'Q' to quit
"""

import pyautogui
import datetime
import os
import sys
import time
import keyboard

# Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create screenshots directory
SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

print("=" * 70)
print("Screenshot Capture Tool")
print("=" * 70)
print()
print("Controls:")
print("  [S] - Capture FULL screen")
print("  [F] - Capture specific REGION (you'll define the area)")
print("  [Q] - Quit")
print()
print("Screenshots will be saved to:", os.path.abspath(SCREENSHOT_DIR))
print()
print("=" * 70)
print()

screenshot_count = 0

def capture_full_screen():
    """Capture full screen"""
    global screenshot_count
    screenshot_count += 1

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}_{screenshot_count}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Capturing full screen...")
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    print(f"[OK] Saved: {filename}")
    print(f"     Size: {screenshot.size[0]} x {screenshot.size[1]}")
    print(f"     Path: {os.path.abspath(filepath)}")
    print()

def capture_region():
    """Capture specific region"""
    global screenshot_count
    screenshot_count += 1

    print()
    print("Define capture region:")
    print("  Move mouse to TOP-LEFT corner and press SPACE")

    # Wait for first position
    while True:
        if keyboard.is_pressed('space'):
            x1, y1 = pyautogui.position()
            print(f"  Top-left: ({x1}, {y1})")
            time.sleep(0.3)  # Debounce
            break
        time.sleep(0.1)

    print("  Move mouse to BOTTOM-RIGHT corner and press SPACE")

    # Wait for second position
    while True:
        if keyboard.is_pressed('space'):
            x2, y2 = pyautogui.position()
            print(f"  Bottom-right: ({x2}, {y2})")
            time.sleep(0.3)  # Debounce
            break
        time.sleep(0.1)

    # Calculate region
    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_region_{timestamp}_{screenshot_count}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Capturing region ({x}, {y}, {width}, {height})...")
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot.save(filepath)

    print(f"[OK] Saved: {filename}")
    print(f"     Size: {screenshot.size[0]} x {screenshot.size[1]}")
    print(f"     Path: {os.path.abspath(filepath)}")
    print()

try:
    print("Ready! Press S/F to capture, Q to quit")
    print()

    while True:
        if keyboard.is_pressed('s'):
            capture_full_screen()
            time.sleep(0.5)  # Debounce

        elif keyboard.is_pressed('f'):
            capture_region()
            time.sleep(0.5)  # Debounce

        elif keyboard.is_pressed('q'):
            print("Quitting...")
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nInterrupted by user")

print()
print("=" * 70)
print(f"Total screenshots captured: {screenshot_count}")
print("=" * 70)
