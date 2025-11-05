# -*- coding: utf-8 -*-
"""
Daily Scenario Runner with Real-time Monitoring
실시간 모니터링과 Daily Scenario 자동화를 실행하는 프로그램
"""

import sys
import os
import json
import datetime
import time
import threading
import pyautogui
import cv2
import numpy as np

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('color')  # ANSI 색상 활성화

from core.monitor import Monitor
from core.automation import Automation


class RealtimeMonitor:
    """실시간 모니터링 클래스 - OpenCV 윈도우 표시"""

    def __init__(self):
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

                # 픽셀 색상
                self.pixel_color = screenshot.getpixel((self.mouse_x, self.mouse_y))

                # 화면 크기 조정 (90%)
                scale = 0.9

                # Detection Area 계산 (실제 화면 좌표)
                box_top_real = int(self.screen_height * 0.5)
                box_bottom_real = self.screen_height - 50
                box_left_real = self.screen_width // 2
                box_right_real = self.screen_width

                # Detection Area만 크롭
                detection_frame = full_frame[box_top_real:box_bottom_real, box_left_real:box_right_real]

                # 크롭된 영역 리사이즈 (50%)
                detection_height = box_bottom_real - box_top_real
                detection_width = box_right_real - box_left_real
                new_detection_width = int(detection_width * scale)
                new_detection_height = int(detection_height * scale)
                frame = cv2.resize(detection_frame, (new_detection_width, new_detection_height))

                # Detection Area 내에서의 상대 마우스 위치 계산
                if box_left_real <= self.mouse_x <= box_right_real and box_top_real <= self.mouse_y <= box_bottom_real:
                    relative_mouse_x = self.mouse_x - box_left_real
                    relative_mouse_y = self.mouse_y - box_top_real
                    scaled_mouse_x = int(relative_mouse_x * scale)
                    scaled_mouse_y = int(relative_mouse_y * scale)
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
                cv2.imshow('Daily Scenario - Detection Area', frame)

                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                    break

                self.update_count += 1

            except Exception as e:
                print(f"\nMonitor error: {e}")
                break

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


class MainRunner:
    """메인 자동화 실행기"""

    def __init__(self, config_path="config.json"):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self.load_config(config_path)
        self.monitor = Monitor()
        self.automation = Automation()
        self.realtime_monitor = RealtimeMonitor()
        self.stories = []
        self.current_story_index = 0

    def load_config(self, config_path):
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠ Config file not found: {config_path}")
            return self.get_default_config()
        except json.JSONDecodeError:
            print(f"⚠ Invalid JSON in config file")
            return self.get_default_config()

    def get_default_config(self):
        """기본 설정"""
        return {
            "enabled_stories": [],
            "story_order": [],
            "monitor_before_start": True,
            "monitor_duration": 5,
            "pause_between_stories": 3,
            "auto_restart": False,
            "realtime_monitor": True
        }

    def log(self, message):
        """로그 출력"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] [MAIN] {message}")

    def initialize_stories(self):
        """스토리 목록 초기화"""
        self.log("Initializing stories...")

        # Daily Scenario Story 추가
        from stories.daily_scenario import DailyScenarioStory

        # Detection Area가 설정될 때까지 대기
        self.log("Waiting for detection area...")
        for _ in range(50):  # 5초 대기
            if self.realtime_monitor.get_detection_area():
                break
            time.sleep(0.1)

        daily_story = DailyScenarioStory()
        detection_area = self.realtime_monitor.get_detection_area()
        if detection_area:
            daily_story.set_detection_area(detection_area)
            self.log(f"Detection area set: {detection_area}")

        self.stories.append(daily_story)

        self.log(f"Total stories loaded: {len(self.stories)}")

    def monitor_before_start(self):
        """시작 전 모니터링"""
        if not self.config.get("monitor_before_start", False):
            return True

        duration = self.config.get("monitor_duration", 5)
        self.log(f"Monitoring for {duration} seconds before start...")

        # 실시간 모니터링 표시
        for i in range(duration * 10):
            self.realtime_monitor.print_status()
            time.sleep(0.1)

        # 화면 안정화 확인
        initial_screenshot = self.monitor.capture()
        time.sleep(1)
        final_screenshot = self.monitor.capture()

        changed, _, diff = self.monitor.detect_screen_change(initial_screenshot, threshold=0.1)

        if changed:
            self.log(f"⚠ Screen is changing (diff: {diff:.4f})")
            self.log("Waiting for screen to stabilize...")
            time.sleep(3)

        self.log("✓ Monitoring complete")
        return True

    def run_story(self, story):
        """단일 스토리 실행"""
        self.log(f"Starting story: {story.name}")

        result = story.run()

        if result:
            self.log(f"✓ Story completed: {story.name}")
        else:
            self.log(f"❌ Story failed: {story.name}")

        return result

    def run_all_stories(self):
        """모든 스토리 순차 실행"""
        self.log("=" * 70)
        self.log("Starting All Stories")
        self.log("=" * 70)

        results = []
        pause = self.config.get("pause_between_stories", 3)

        for i, story in enumerate(self.stories):
            self.current_story_index = i

            self.log(f"\n[{i+1}/{len(self.stories)}] Running: {story.name}")

            result = self.run_story(story)
            results.append({
                "name": story.name,
                "status": story.status,
                "success": result
            })

            # 다음 스토리 전 대기
            if i < len(self.stories) - 1:
                self.log(f"Waiting {pause} seconds before next story...")
                for _ in range(pause * 10):
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)

        return results

    def print_summary(self, results):
        """결과 요약 출력"""
        self.log("\n" + "=" * 70)
        self.log("Execution Summary")
        self.log("=" * 70)

        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        for i, result in enumerate(results, 1):
            status_icon = "✓" if result["success"] else "❌"
            self.log(f"{i}. {status_icon} {result['name']} - {result['status']}")

        self.log("=" * 70)
        self.log(f"Success: {success_count}/{total_count}")
        self.log("=" * 70)

    def run(self):
        """메인 실행"""
        try:
            # 실시간 모니터 시작
            if self.config.get("realtime_monitor", True):
                self.realtime_monitor.start()
                self.log("✓ Realtime monitor started")

            self.log("=" * 70)
            self.log("Mabinogi Mobile Auto - Daily Scenario Runner")
            self.log("=" * 70)

            # 스토리 초기화
            self.initialize_stories()

            if not self.stories:
                self.log("⚠ No stories loaded.")
                self.log("화면 모니터링만 실행합니다. (Ctrl+C로 종료)")

                # 스토리가 없으면 모니터링만 계속
                while True:
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)
                return

            # 시작 전 모니터링
            self.monitor_before_start()

            # 모든 스토리 실행
            results = self.run_all_stories()

            # 결과 요약
            self.print_summary(results)

            # 자동 재시작
            if self.config.get("auto_restart", False):
                self.log("\n⚠ Auto-restart is enabled")
                self.log("Restarting in 10 seconds...")
                for _ in range(100):
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)
                self.run()  # 재귀 실행

        except KeyboardInterrupt:
            self.log("\n⚠ Interrupted by user")
        except Exception as e:
            self.log(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.realtime_monitor.stop()


def main():
    """진입점"""
    print("=" * 80)
    print(" " * 15 + "Mabinogi Mobile Auto - Daily Scenario")
    print("=" * 80)
    print()
    print("  📺 실시간 화면 모니터링 + Daily Scenario 자동화")
    print()
    print("  ✓ 게임시작 버튼 클릭")
    print("  ✓ 은동전 최대 캐릭터 선택")
    print("  ✓ 게임시작(노란색) 버튼 클릭")
    print()
    print("  종료: Ctrl+C 또는 Q 키")
    print("=" * 80)
    print()

    # 3초 후 시작
    print("3초 후 시작합니다...")
    for i in range(3, 0, -1):
        print(f"  {i}...", end="\r")
        time.sleep(1)
    print("  시작!     ")
    print()

    # 실행
    runner = MainRunner()
    runner.run()


if __name__ == "__main__":
    main()
