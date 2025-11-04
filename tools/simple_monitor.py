# -*- coding: utf-8 -*-
"""
Enhanced Real-time Monitor
실시간 화면 모니터링 with 향상된 UI
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
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create screenshots directory
SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def draw_text_with_background(img, text, pos, font_scale=0.6, thickness=2,
                               text_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """배경이 있는 텍스트 그리기"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = pos
    # 배경 사각형
    cv2.rectangle(img,
                  (x - 5, y - text_height - 5),
                  (x + text_width + 5, y + baseline + 5),
                  bg_color, -1)
    # 테두리
    cv2.rectangle(img,
                  (x - 5, y - text_height - 5),
                  (x + text_width + 5, y + baseline + 5),
                  (100, 100, 100), 1)
    # 텍스트
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

    return text_height + baseline + 15

print("=" * 70)
print("Enhanced Real-time Monitor")
print("=" * 70)
print()
print("Controls:")
print("  [S] - Save screenshot")
print("  [C] - Toggle crosshair")
print("  [Q] - Quit")
print()
print("Opening monitor window...")
print("=" * 70)

frame_count = 0
screenshot_count = 0
start_time = time.time()
fps_list = []
show_crosshair = True

try:
    while True:
        loop_start = time.time()
        frame_count += 1

        # 마우스 위치 가져오기
        mouse_x, mouse_y = pyautogui.position()

        # 화면 캡처
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 마우스 위치의 픽셀 색상
        pixel_color = screenshot.getpixel((mouse_x, mouse_y))

        # 화면 크기 조정
        height, width = frame.shape[:2]
        scale = 0.5
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height))

        # 스케일된 마우스 위치
        scaled_mouse_x = int(mouse_x * scale)
        scaled_mouse_y = int(mouse_y * scale)

        # FPS 계산
        loop_time = time.time() - loop_start
        current_fps = 1.0 / loop_time if loop_time > 0 else 0
        fps_list.append(current_fps)
        if len(fps_list) > 30:
            fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)

        # 경과 시간
        elapsed = time.time() - start_time
        elapsed_str = str(datetime.timedelta(seconds=int(elapsed)))

        # 십자선 그리기
        if show_crosshair:
            # 가로선
            cv2.line(frame, (0, scaled_mouse_y), (new_width, scaled_mouse_y), (0, 255, 255), 1)
            # 세로선
            cv2.line(frame, (scaled_mouse_x, 0), (scaled_mouse_x, new_height), (0, 255, 255), 1)
            # 중앙 원
            cv2.circle(frame, (scaled_mouse_x, scaled_mouse_y), 10, (0, 255, 255), 2)
            cv2.circle(frame, (scaled_mouse_x, scaled_mouse_y), 2, (0, 255, 255), -1)

        # 정보 패널 배경
        panel_height = 280
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (400, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # 정보 표시
        y_offset = 25

        # 제목
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        y_offset += draw_text_with_background(frame, f"MONITOR - {timestamp}",
                                               (10, y_offset), 0.5, 1,
                                               (0, 255, 255), (0, 50, 100))

        # 마우스 정보
        y_offset += draw_text_with_background(frame, "=== MOUSE ===",
                                               (10, y_offset), 0.5, 1,
                                               (255, 200, 0), (0, 0, 0))
        y_offset += draw_text_with_background(frame, f"Position: ({mouse_x}, {mouse_y})",
                                               (10, y_offset), 0.5, 1)
        y_offset += draw_text_with_background(frame, f"RGB: {pixel_color}",
                                               (10, y_offset), 0.5, 1)
        y_offset += draw_text_with_background(frame, f"HEX: #{pixel_color[0]:02X}{pixel_color[1]:02X}{pixel_color[2]:02X}",
                                               (10, y_offset), 0.5, 1)

        # 시스템 정보
        y_offset += 10
        y_offset += draw_text_with_background(frame, "=== SYSTEM ===",
                                               (10, y_offset), 0.5, 1,
                                               (255, 200, 0), (0, 0, 0))
        y_offset += draw_text_with_background(frame, f"FPS: {avg_fps:.1f}",
                                               (10, y_offset), 0.5, 1)
        y_offset += draw_text_with_background(frame, f"Frame: {frame_count}",
                                               (10, y_offset), 0.5, 1)
        y_offset += draw_text_with_background(frame, f"Elapsed: {elapsed_str}",
                                               (10, y_offset), 0.5, 1)

        # 스크린샷 정보
        y_offset += 10
        y_offset += draw_text_with_background(frame, "=== CAPTURE ===",
                                               (10, y_offset), 0.5, 1,
                                               (255, 200, 0), (0, 0, 0))
        y_offset += draw_text_with_background(frame, f"Screenshots: {screenshot_count}",
                                               (10, y_offset), 0.5, 1)
        y_offset += draw_text_with_background(frame, f"Resolution: {width}x{height}",
                                               (10, y_offset), 0.5, 1)

        # 색상 프리뷰 (우측 상단)
        color_preview_size = 80
        color_preview = np.zeros((color_preview_size, color_preview_size, 3), dtype=np.uint8)
        color_preview[:, :] = (pixel_color[2], pixel_color[1], pixel_color[0])  # RGB to BGR
        frame[10:10+color_preview_size, new_width-color_preview_size-10:new_width-10] = color_preview
        cv2.rectangle(frame, (new_width-color_preview_size-10, 10),
                     (new_width-10, 10+color_preview_size), (255, 255, 255), 2)

        # 컨트롤 안내 (하단)
        controls_y = new_height - 30
        draw_text_with_background(frame, "[S]Save [C]Crosshair [Q]Quit",
                                  (10, controls_y), 0.5, 1,
                                  (255, 255, 0), (50, 50, 50))

        # 화면 표시
        cv2.imshow('Enhanced Monitor', frame)

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s') or key == ord('S'):
            # 스크린샷 저장
            screenshot_count += 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitor_{timestamp}_{screenshot_count}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)

            original_screenshot = pyautogui.screenshot()
            original_screenshot.save(filepath)

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Screenshot saved: {filename}")

        elif key == ord('c') or key == ord('C'):
            # 십자선 토글
            show_crosshair = not show_crosshair
            status = "ON" if show_crosshair else "OFF"
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Crosshair: {status}")

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
    print(f"Average FPS: {sum(fps_list) / len(fps_list) if fps_list else 0:.1f}")
    print("=" * 70)
