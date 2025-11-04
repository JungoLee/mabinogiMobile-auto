# -*- coding: utf-8 -*-
"""
Main Automation with Real-time Monitor
자동화 실행과 동시에 실시간 모니터링
"""

import sys
import os
import json
import datetime
import threading
import time
import cv2
import numpy as np
import pyautogui

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.monitor import Monitor
from core.automation import Automation
from core.click_tracker import ClickTracker

# 스토리 임포트
from stories.quest_story import QuestStory
from stories.trade_story import TradeStory
from stories.daily_story import DailyStory


class MonitorThread(threading.Thread):
    """실시간 모니터링 스레드"""

    def __init__(self):
        super().__init__(daemon=True)
        self.running = True
        self.screenshot_count = 0
        self.screenshot_dir = "screenshots"
        self.show_crosshair = True
        self.automation_status = "대기"
        self.current_story = ""
        self.story_progress = ""
        self.click_tracker = ClickTracker()  # 클릭 추적기 (automation과 공유)
        self.story_trigger = None  # 스토리 실행 트리거
        self.buttons = []  # 버튼 목록 [(x, y, width, height, label, story_name), ...]
        self.paused = False  # 일시정지 상태

        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def draw_text_with_background(self, img, text, pos, font_scale=0.6, thickness=2,
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

    def update_status(self, status, story="", progress=""):
        """자동화 상태 업데이트"""
        self.automation_status = status
        self.current_story = story
        self.story_progress = progress

    def draw_button(self, img, x, y, width, height, text, bg_color=(50, 50, 50),
                    text_color=(255, 255, 255), border_color=(100, 100, 100)):
        """버튼 그리기"""
        # 버튼 배경
        cv2.rectangle(img, (x, y), (x + width, y + height), bg_color, -1)
        # 버튼 테두리
        cv2.rectangle(img, (x, y), (x + width, y + height), border_color, 2)

        # 텍스트 중앙 정렬
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.40  # 0.45에서 0.40으로 감소
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = x + (width - text_width) // 2
        text_y = y + (height + text_height) // 2

        cv2.putText(img, text, (text_x, text_y), font, font_scale, text_color, thickness)

    def mouse_callback(self, event, x, y, flags, param):
        """마우스 클릭 콜백 - 버튼 클릭 처리"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # 버튼 클릭 확인
            for btn_x, btn_y, btn_w, btn_h, btn_label, story_name in self.buttons:
                if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                    print(f"[모니터] 버튼 클릭: {btn_label}")
                    self.story_trigger = story_name
                    return

    def run(self):
        """모니터링 루프"""
        frame_count = 0
        start_time = time.time()
        fps_list = []

        print("[모니터] 실시간 모니터 시작 중...")

        # OpenCV 창 생성 및 마우스 콜백 설정
        cv2.namedWindow('Automation Monitor')
        cv2.setMouseCallback('Automation Monitor', self.mouse_callback)

        # 버튼 정의 (x, y, width, height, label, story_name)
        # 화면이 60% 스케일이므로 실제 좌표의 0.6배
        button_y_start = 162  # 270을 60%로 조정
        button_spacing = 45
        self.buttons = [
            (10, button_y_start, 140, 35, "Quest Story", "quest"),
            (160, button_y_start, 140, 35, "Trade Story", "trade"),
            (310, button_y_start, 140, 35, "Daily Story", "daily"),
        ]

        try:
            while self.running:
                loop_start = time.time()
                frame_count += 1

                # 마우스 위치
                mouse_x, mouse_y = pyautogui.position()

                # 화면 캡처
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # 화면 크기
                height, width = frame.shape[:2]

                # 픽셀 색상 (범위 체크)
                if 0 <= mouse_x < width and 0 <= mouse_y < height:
                    pixel_color = screenshot.getpixel((mouse_x, mouse_y))
                else:
                    pixel_color = (0, 0, 0)  # 화면 밖이면 검은색

                # 화면 크기 조정 (50%에서 60%로 증가)
                scale = 0.6
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

                # 클릭 영역 가이드 (화면의 50%~100% 영역을 빨간 네모로 표시)
                guide_x1 = int(new_width * 0.5)  # 50% 지점
                guide_y1 = int(new_height * 0.5)  # 50% 지점
                guide_x2 = new_width  # 100%
                guide_y2 = new_height  # 100%
                cv2.rectangle(frame, (guide_x1, guide_y1), (guide_x2, guide_y2), (0, 0, 255), 2)

                # 십자선 그리기
                if self.show_crosshair:
                    cv2.line(frame, (0, scaled_mouse_y), (new_width, scaled_mouse_y), (0, 255, 255), 1)
                    cv2.line(frame, (scaled_mouse_x, 0), (scaled_mouse_x, new_height), (0, 255, 255), 1)
                    cv2.circle(frame, (scaled_mouse_x, scaled_mouse_y), 10, (0, 255, 255), 2)
                    cv2.circle(frame, (scaled_mouse_x, scaled_mouse_y), 2, (0, 255, 255), -1)

                # 자동화 클릭 마크 그리기 (3초 동안 표시)
                current_time = time.time()
                recent_clicks = self.click_tracker.get_recent_clicks()

                # 클릭 마크 그리기
                for click_x, click_y, click_time in recent_clicks:
                    # 스케일 적용 (실제 좌표를 모니터 좌표로 변환)
                    mark_x = int(click_x * scale)
                    mark_y = int(click_y * scale)

                    # 시간 경과
                    elapsed_time = current_time - click_time
                    alpha = 1.0 - (elapsed_time / 3.0)

                    # 빨간 점 (중심)
                    cv2.circle(frame, (mark_x, mark_y), 5, (0, 0, 255), -1)
                    # 외곽 원 (크기가 시간에 따라 커짐)
                    radius = int(10 + (elapsed_time * 10))
                    cv2.circle(frame, (mark_x, mark_y), radius, (0, 0, 255), 2)
                    # X 표시
                    size = 8
                    cv2.line(frame, (mark_x - size, mark_y - size), (mark_x + size, mark_y + size), (0, 0, 255), 2)
                    cv2.line(frame, (mark_x + size, mark_y - size), (mark_x - size, mark_y + size), (0, 0, 255), 2)

                # 정보 패널 배경 (버튼 공간 포함)
                panel_height = 310
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (460, panel_height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

                # 정보 표시
                y_offset = 25
                font_size = 0.42  # 폰트 크기 더 감소

                # 제목
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                y_offset += self.draw_text_with_background(frame, f"AUTO MONITOR - {timestamp}",
                                                           (10, y_offset), font_size, 1,
                                                           (0, 255, 255), (0, 50, 100))

                # 자동화 상태 (영문 매핑)
                status_map = {
                    "대기": "Idle",
                    "준비완료": "Ready",
                    "실행중": "Running",
                    "대기중": "Waiting",
                    "완료": "Completed",
                    "일시정지": "PAUSED"
                }
                status_en = status_map.get(self.automation_status, self.automation_status)

                # 상태 색상
                if self.automation_status == "실행중":
                    status_color = (0, 255, 0)  # 초록색
                elif self.automation_status == "일시정지":
                    status_color = (0, 165, 255)  # 주황색 (일시정지)
                else:
                    status_color = (255, 200, 0)  # 노란색
                y_offset += self.draw_text_with_background(frame, "=== AUTOMATION ===",
                                                           (10, y_offset), font_size, 1,
                                                           (255, 200, 0), (0, 0, 0))
                y_offset += self.draw_text_with_background(frame, f"Status: {status_en}",
                                                           (10, y_offset), font_size, 1, status_color)
                if self.current_story:
                    y_offset += self.draw_text_with_background(frame, f"Story: {self.current_story}",
                                                               (10, y_offset), font_size, 1)
                if self.story_progress:
                    y_offset += self.draw_text_with_background(frame, f"Step: {self.story_progress}",
                                                               (10, y_offset), font_size, 1)

                # 마우스 정보
                y_offset += 10
                y_offset += self.draw_text_with_background(frame, "=== MOUSE ===",
                                                           (10, y_offset), font_size, 1,
                                                           (255, 200, 0), (0, 0, 0))
                y_offset += self.draw_text_with_background(frame, f"Position: ({mouse_x}, {mouse_y})",
                                                           (10, y_offset), font_size, 1)
                y_offset += self.draw_text_with_background(frame, f"RGB: {pixel_color}",
                                                           (10, y_offset), font_size, 1)
                y_offset += self.draw_text_with_background(frame, f"HEX: #{pixel_color[0]:02X}{pixel_color[1]:02X}{pixel_color[2]:02X}",
                                                           (10, y_offset), font_size, 1)

                # FPS 및 경과 시간
                y_offset += 10
                y_offset += self.draw_text_with_background(frame, f"FPS: {avg_fps:.1f}  Elapsed: {elapsed_str}",
                                                           (10, y_offset), font_size, 1)

                # 버튼 그리기
                for btn_x, btn_y, btn_w, btn_h, btn_label, story_name in self.buttons:
                    # 버튼 색상 (현재 실행 중인 스토리면 초록색)
                    if self.current_story and story_name in self.current_story.lower():
                        bg_color = (0, 100, 0)  # 초록색
                        border_color = (0, 200, 0)
                    else:
                        bg_color = (50, 50, 50)  # 회색
                        border_color = (100, 100, 100)

                    self.draw_button(frame, btn_x, btn_y, btn_w, btn_h, btn_label,
                                   bg_color=bg_color, border_color=border_color)

                # 색상 프리뷰 (우측 상단)
                color_preview_size = 80
                color_preview = np.zeros((color_preview_size, color_preview_size, 3), dtype=np.uint8)
                color_preview[:, :] = (pixel_color[2], pixel_color[1], pixel_color[0])
                frame[10:10+color_preview_size, new_width-color_preview_size-10:new_width-10] = color_preview
                cv2.rectangle(frame, (new_width-color_preview_size-10, 10),
                             (new_width-10, 10+color_preview_size), (255, 255, 255), 2)

                # 컨트롤 안내 (하단)
                controls_y = new_height - 30
                pause_text = "[Paused]" if self.paused else ""
                control_text = f"[ESC]Pause/Resume {pause_text}  [Ctrl+C]Quit"
                control_color = (0, 165, 255) if self.paused else (255, 255, 0)
                self.draw_text_with_background(frame, control_text,
                                              (10, controls_y), font_size, 1,
                                              control_color, (50, 50, 50))

                # 화면 표시
                cv2.imshow('Automation Monitor', frame)

                # OpenCV 창이 닫혔는지 확인
                if cv2.getWindowProperty('Automation Monitor', cv2.WND_PROP_VISIBLE) < 1:
                    print("[모니터] 창이 외부에서 닫혔습니다")
                    self.running = False
                    break

                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF

                # ESC 키로 일시정지/재개
                if key == 27:  # ESC 키
                    self.paused = not self.paused
                    status_text = "일시정지됨" if self.paused else "재개됨"
                    print(f"[모니터] 자동화 {status_text}")
                    if self.paused:
                        self.update_status("일시정지", self.current_story, "Paused by user")
                    else:
                        self.update_status("실행중", self.current_story, "Resumed")

            print(f"[모니터] While 루프 종료됨. Running flag: {self.running}, Frame count: {frame_count}")

        except Exception as e:
            print(f"[모니터] 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            print(f"[모니터] 상세 오류 정보:")
            print(f"  - Frame count: {frame_count}")
            print(f"  - Running flag: {self.running}")
        finally:
            cv2.destroyAllWindows()
            print("[모니터] 모니터 중지됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False


class MainRunner:
    """메인 자동화 실행기 with 모니터"""

    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.monitor = Monitor()
        self.automation = Automation()
        self.stories = []
        self.current_story_index = 0
        self.monitor_thread = None

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
            "enabled_stories": ["quest", "trade", "daily"],
            "story_order": ["quest", "trade", "daily"],
            "monitor_before_start": False,
            "monitor_duration": 5,
            "pause_between_stories": 3,
            "auto_restart": False
        }

    def log(self, message):
        """로그 출력"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [메인] {message}")

    def initialize_stories(self):
        """스토리 목록 초기화"""
        self.log("스토리 초기화 중...")

        story_map = {
            "quest": QuestStory,
            "trade": TradeStory,
            "daily": DailyStory
        }

        enabled = self.config.get("enabled_stories", [])
        order = self.config.get("story_order", [])

        for story_name in order:
            if story_name in enabled and story_name in story_map:
                story_class = story_map[story_name]
                self.stories.append(story_class())
                self.log(f"✓ 로드 완료: {story_name}")

        self.log(f"총 {len(self.stories)}개 스토리 로드됨")

    def run_story(self, story):
        """단일 스토리 실행"""
        self.log(f"스토리 시작: {story.name}")

        if self.monitor_thread:
            self.monitor_thread.update_status("실행중", story.name, "Starting...")

        result = story.run()

        if result:
            self.log(f"✓ 스토리 완료: {story.name}")
        else:
            self.log(f"❌ 스토리 실패: {story.name}")

        if self.monitor_thread:
            self.monitor_thread.update_status("완료", story.name, "Finished")

        return result

    def run_story_by_name(self, story_name):
        """이름으로 스토리 실행"""
        story_map = {
            "quest": QuestStory,
            "trade": TradeStory,
            "daily": DailyStory
        }

        if story_name not in story_map:
            self.log(f"❌ 알 수 없는 스토리: {story_name}")
            return False

        self.log(f"버튼으로 스토리 시작: {story_name}")
        story = story_map[story_name]()
        return self.run_story(story)

    def run_all_stories(self):
        """모든 스토리 순차 실행"""
        self.log("=" * 70)
        self.log("모든 스토리 시작")
        self.log("=" * 70)

        results = []
        pause = self.config.get("pause_between_stories", 3)

        for i, story in enumerate(self.stories):
            self.current_story_index = i

            self.log(f"\n[{i+1}/{len(self.stories)}] 실행중: {story.name}")

            result = self.run_story(story)
            results.append({
                "name": story.name,
                "status": story.status,
                "success": result
            })

            if i < len(self.stories) - 1:
                self.log(f"다음 스토리까지 {pause}초 대기 중...")
                if self.monitor_thread:
                    self.monitor_thread.update_status("대기중", "", f"Next in {pause}s")
                time.sleep(pause)

        return results

    def print_summary(self, results):
        """결과 요약 출력"""
        self.log("\n" + "=" * 70)
        self.log("실행 결과 요약")
        self.log("=" * 70)

        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        for i, result in enumerate(results, 1):
            status_icon = "✓" if result["success"] else "❌"
            self.log(f"{i}. {status_icon} {result['name']} - {result['status']}")

        self.log("=" * 70)
        self.log(f"성공: {success_count}/{total_count}")
        self.log("=" * 70)

    def run(self):
        """메인 실행"""
        try:
            self.log("=" * 70)
            self.log("마비노기 모바일 자동화 - 모니터링 모드")
            self.log("=" * 70)

            # 모니터 스레드 시작
            self.monitor_thread = MonitorThread()
            self.monitor_thread.start()
            self.log("실시간 모니터 시작됨")
            time.sleep(1)  # 모니터 초기화 대기

            # 스토리 초기화
            self.initialize_stories()

            if not self.stories:
                self.log("❌ 로드된 스토리가 없습니다. config.json을 확인하세요")
                return

            self.monitor_thread.update_status("준비완료", "", "Starting automation...")
            time.sleep(2)

            # 모든 스토리 실행
            results = self.run_all_stories()

            # 결과 요약
            self.print_summary(results)

            if self.monitor_thread:
                success_count = sum(1 for r in results if r['success'])
                total_count = len(results)
                self.monitor_thread.update_status("완료", "", f"{success_count}/{total_count} Success")

            # 모니터 창이 열려있는 동안 대기
            self.log("\n" + "=" * 70)
            self.log("자동화 완료!")
            self.log("모니터 창이 계속 실행 중입니다.")
            self.log("모니터 창에서 Q를 누르거나 Ctrl+C로 종료하세요.")
            self.log("=" * 70)

            # 모니터 스레드가 종료될 때까지 대기 (버튼 클릭 감지)
            while self.monitor_thread and self.monitor_thread.is_alive():
                # 일시정지 상태 확인
                if self.monitor_thread.paused:
                    time.sleep(0.5)
                    continue

                # 버튼 클릭으로 스토리 실행 요청 확인
                if self.monitor_thread.story_trigger:
                    story_name = self.monitor_thread.story_trigger
                    self.monitor_thread.story_trigger = None  # 트리거 초기화

                    self.log(f"\n[버튼] {story_name} 스토리 실행 요청됨")
                    self.run_story_by_name(story_name)

                time.sleep(0.5)  # 0.5초마다 체크

            # 자동 재시작
            if self.config.get("auto_restart", False):
                self.log("\n⚠ 자동 재시작이 활성화되어 있습니다")
                self.log("10초 후 재시작합니다...")
                time.sleep(10)
                self.run()

        except KeyboardInterrupt:
            self.log("\n⚠ 사용자가 중단했습니다")
        except Exception as e:
            self.log(f"\n❌ 치명적 오류: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.monitor_thread:
                self.monitor_thread.stop()
                self.monitor_thread.join(timeout=2)


def main():
    """진입점"""
    print("=" * 70)
    print("마비노기 모바일 자동화 - 실시간 모니터링")
    print("=" * 70)
    print()
    print("이 프로그램은 자동화와 모니터링을 동시에 실행합니다:")
    print("  - 자동화: 퀘스트, 물물교환, 주간컨텐츠 스토리 순차 실행")
    print("  - 모니터: 실시간 화면 모니터링 (별도 창)")
    print()
    print("모니터 컨트롤:")
    print("  [S] - 스크린샷 저장")
    print("  [C] - 십자선 토글")
    print("  [Q] - 종료")
    print()
    print("종료하려면 Ctrl+C를 누르거나 모니터 창에서 Q를 누르세요")
    print("=" * 70)
    print()

    # 3초 후 시작
    print("3초 후 시작합니다...")
    time.sleep(3)

    # 실행
    runner = MainRunner()
    runner.run()


if __name__ == "__main__":
    main()
