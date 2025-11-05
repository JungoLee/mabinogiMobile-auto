# -*- coding: utf-8 -*-
"""
Realtime Monitor Component
실시간 모니터링 컴포넌트 - 공통 사용
"""

import sys
import threading
import time
import pyautogui
import cv2
import numpy as np

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class RealtimeMonitor:
    """실시간 모니터링 클래스 - OpenCV 윈도우 표시"""

    def __init__(self, window_title="Real-time Monitor", scale=0.8):
        """
        Args:
            window_title: OpenCV 윈도우 제목
            scale: 화면 스케일 (0.0 ~ 1.0, 기본: 0.8 = 80%)
        """
        self.window_title = window_title
        self.scale = scale
        self.running = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.pixel_color = (0, 0, 0)
        self.screen_width = 0
        self.screen_height = 0
        self.update_count = 0
        self.show_window = True

        # 작업 영역 (Detection Area)
        self.detection_area = None  # (x1, y1, x2, y2)

    def start(self):
        """모니터링 시작"""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()

    def stop(self):
        """모니터링 중지"""
        self.running = False
        cv2.destroyAllWindows()

    def _monitor_loop(self):
        """모니터링 루프 (별도 스레드) - OpenCV 윈도우 표시"""
        while self.running:
            try:
                # 마우스 위치
                self.mouse_x, self.mouse_y = pyautogui.position()

                # 화면 크기
                self.screen_width, self.screen_height = pyautogui.size()

                # 화면 캡처
                screenshot = pyautogui.screenshot()
                full_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # 픽셀 색상 (마우스가 화면 범위 내에 있을 때만)
                if 0 <= self.mouse_x < self.screen_width and 0 <= self.mouse_y < self.screen_height:
                    self.pixel_color = screenshot.getpixel((self.mouse_x, self.mouse_y))
                # 범위 밖이면 이전 색상 유지

                # Detection Area 계산 (실제 화면 좌표)
                box_top_real = int(self.screen_height * 0.5)
                box_bottom_real = self.screen_height - 50
                box_left_real = self.screen_width // 2
                box_right_real = self.screen_width

                # Detection Area만 크롭
                detection_frame = full_frame[box_top_real:box_bottom_real, box_left_real:box_right_real]

                # 크롭된 영역 리사이즈 (scale%)
                detection_height = box_bottom_real - box_top_real
                detection_width = box_right_real - box_left_real
                new_detection_width = int(detection_width * self.scale)
                new_detection_height = int(detection_height * self.scale)
                frame = cv2.resize(detection_frame, (new_detection_width, new_detection_height))

                # Detection Area 내에서의 상대 마우스 위치 계산
                if box_left_real <= self.mouse_x <= box_right_real and box_top_real <= self.mouse_y <= box_bottom_real:
                    relative_mouse_x = self.mouse_x - box_left_real
                    relative_mouse_y = self.mouse_y - box_top_real
                    scaled_mouse_x = int(relative_mouse_x * self.scale)
                    scaled_mouse_y = int(relative_mouse_y * self.scale)
                else:
                    scaled_mouse_x = -100  # 영역 밖
                    scaled_mouse_y = -100

                # 십자선 그리기 (마우스가 영역 안에 있을 때만)
                if scaled_mouse_x >= 0 and scaled_mouse_y >= 0:
                    cv2.line(frame, (0, scaled_mouse_y), (new_detection_width, scaled_mouse_y), (0, 255, 255), 1)
                    cv2.line(frame, (scaled_mouse_x, 0), (scaled_mouse_x, new_detection_height), (0, 255, 255), 1)
                    cv2.circle(frame, (scaled_mouse_x, scaled_mouse_y), 10, (0, 255, 255), 2)

                # 정보 표시
                hex_color = f"#{self.pixel_color[0]:02X}{self.pixel_color[1]:02X}{self.pixel_color[2]:02X}"

                # 반투명 배경
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (500, 120), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

                # 텍스트 정보
                y_offset = 25
                cv2.putText(frame, f"Mouse: ({self.mouse_x}, {self.mouse_y})",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                cv2.putText(frame, f"RGB: {self.pixel_color}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                cv2.putText(frame, f"HEX: {hex_color}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                cv2.putText(frame, f"Screen: {self.screen_width}x{self.screen_height} | [Q] Quit",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                # 색상 프리뷰 (우측 상단)
                color_size = 80
                color_preview = np.zeros((color_size, color_size, 3), dtype=np.uint8)
                color_preview[:, :] = (self.pixel_color[2], self.pixel_color[1], self.pixel_color[0])

                # 색상 프리뷰가 프레임 크기를 넘지 않도록 체크
                if new_detection_width > color_size + 20 and new_detection_height > color_size + 20:
                    frame[10:10+color_size, new_detection_width-color_size-10:new_detection_width-10] = color_preview
                    cv2.rectangle(frame, (new_detection_width-color_size-10, 10),
                                 (new_detection_width-10, 10+color_size), (255, 255, 255), 2)

                # Detection Area 좌표 저장 (실제 화면 좌표)
                self.detection_area = (
                    box_left_real,  # x1
                    box_top_real,   # y1
                    box_right_real, # x2
                    box_bottom_real # y2
                )

                # 화면 표시 (Detection Area Only)
                cv2.imshow(self.window_title, frame)

                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                    break

                self.update_count += 1

            except Exception as e:
                print(f"\nMonitor error: {e}")
                import traceback
                traceback.print_exc()
                # 에러가 발생해도 계속 실행
                time.sleep(0.1)

    def get_status(self):
        """현재 상태 반환"""
        hex_color = f"#{self.pixel_color[0]:02X}{self.pixel_color[1]:02X}{self.pixel_color[2]:02X}"
        return {
            'mouse_pos': (self.mouse_x, self.mouse_y),
            'pixel_color': self.pixel_color,
            'hex_color': hex_color,
            'screen_size': (self.screen_width, self.screen_height),
            'update_count': self.update_count,
            'detection_area': self.detection_area
        }

    def get_detection_area(self):
        """작업 영역 좌표 반환 (x1, y1, x2, y2)"""
        return self.detection_area

    def is_in_detection_area(self, x, y):
        """좌표가 작업 영역 안에 있는지 확인"""
        if self.detection_area is None:
            return False
        x1, y1, x2, y2 = self.detection_area
        return x1 <= x <= x2 and y1 <= y <= y2

    def print_status(self):
        """상태를 한 줄로 출력"""
        status = self.get_status()
        print(f"\r[모니터] 마우스: ({status['mouse_pos'][0]:4d}, {status['mouse_pos'][1]:4d}) | "
              f"RGB: {status['pixel_color']} | HEX: {status['hex_color']} | "
              f"화면: {status['screen_size'][0]}x{status['screen_size'][1]}", end="", flush=True)
