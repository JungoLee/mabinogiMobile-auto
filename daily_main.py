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

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('color')  # ANSI 색상 활성화

from core.monitor import Monitor
from core.automation import Automation
from core.realtime_monitor import RealtimeMonitor


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
        self.realtime_monitor = RealtimeMonitor(
            window_title="Daily Scenario - Detection Area",
            scale=0.9
        )
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
                time.sleep(0.5)  # 모니터 초기화 대기

            self.log("=" * 70)
            self.log("Mabinogi Mobile Auto - Daily Scenario Runner")
            self.log("=" * 70)

            # 스토리 초기화
            self.initialize_stories()

            if not self.stories:
                self.log("⚠ No stories loaded.")
                self.log("화면 모니터링만 실행합니다. (Q 키 또는 Ctrl+C로 종료)")

                # 스토리가 없으면 모니터링만 계속
                while self.realtime_monitor.running:
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)
                return

            # 시작 전 모니터링
            self.monitor_before_start()

            # 모든 스토리 실행
            results = self.run_all_stories()

            # 결과 요약
            self.print_summary(results)

            # 스토리 완료 후에도 모니터 유지
            self.log("\n" + "=" * 70)
            self.log("✓ 모든 스토리 실행 완료")
            self.log("화면 모니터는 계속 실행 중입니다. (Q 키 또는 Ctrl+C로 종료)")
            self.log("=" * 70)

            # 자동 재시작이 아니면 모니터만 유지
            if self.config.get("auto_restart", False):
                self.log("\n⚠ Auto-restart is enabled")
                self.log("Restarting in 10 seconds...")
                for _ in range(100):
                    if not self.realtime_monitor.running:
                        break
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)
                if self.realtime_monitor.running:
                    self.run()  # 재귀 실행
            else:
                # 모니터가 종료될 때까지 대기
                while self.realtime_monitor.running:
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)

        except KeyboardInterrupt:
            self.log("\n⚠ Interrupted by user")
        except Exception as e:
            self.log(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()

            # 에러 발생 시에도 모니터 유지
            self.log("\n" + "=" * 70)
            self.log("에러가 발생했지만 모니터는 계속 실행됩니다.")
            self.log("Q 키 또는 Ctrl+C로 종료하세요.")
            self.log("=" * 70)

            # 모니터가 종료될 때까지 대기
            while self.realtime_monitor.running:
                try:
                    self.realtime_monitor.print_status()
                    time.sleep(0.1)
                except:
                    break
        finally:
            # 최종 정리
            if self.realtime_monitor.running:
                self.realtime_monitor.stop()
            self.log("\n프로그램 종료")


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
