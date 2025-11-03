# -*- coding: utf-8 -*-
"""
Main Automation Runner
모니터링 후 스토리를 순차적으로 실행하는 메인 프로그램
"""

import sys
import os
import json
import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.monitor import Monitor
from core.automation import Automation

# 스토리 임포트
from stories.quest_story import QuestStory
from stories.trade_story import TradeStory
from stories.daily_story import DailyStory


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
            "enabled_stories": ["quest", "trade", "daily"],
            "story_order": ["quest", "trade", "daily"],
            "monitor_before_start": True,
            "monitor_duration": 5,
            "pause_between_stories": 3,
            "auto_restart": False
        }

    def log(self, message):
        """로그 출력"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [MAIN] {message}")

    def initialize_stories(self):
        """스토리 목록 초기화"""
        self.log("Initializing stories...")

        # 사용 가능한 스토리 맵
        story_map = {
            "quest": QuestStory,
            "trade": TradeStory,
            "daily": DailyStory
        }

        # 설정에 따라 스토리 로드
        enabled = self.config.get("enabled_stories", [])
        order = self.config.get("story_order", [])

        for story_name in order:
            if story_name in enabled and story_name in story_map:
                story_class = story_map[story_name]
                self.stories.append(story_class())
                self.log(f"✓ Loaded: {story_name}")

        self.log(f"Total stories loaded: {len(self.stories)}")

    def monitor_before_start(self):
        """시작 전 모니터링"""
        if not self.config.get("monitor_before_start", False):
            return True

        duration = self.config.get("monitor_duration", 5)
        self.log(f"Monitoring for {duration} seconds before start...")

        # 화면 안정화 확인
        import time
        initial_screenshot = self.monitor.capture()
        time.sleep(duration)
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
                import time
                time.sleep(pause)

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
            self.log("=" * 70)
            self.log("Mabinogi Mobile Auto - Main Runner")
            self.log("=" * 70)

            # 스토리 초기화
            self.initialize_stories()

            if not self.stories:
                self.log("❌ No stories loaded. Check config.json")
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
                import time
                time.sleep(10)
                self.run()  # 재귀 실행

        except KeyboardInterrupt:
            self.log("\n⚠ Interrupted by user")
        except Exception as e:
            self.log(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """진입점"""
    print("=" * 70)
    print("Mabinogi Mobile Auto")
    print("=" * 70)
    print()
    print("이 프로그램은 다음 스토리를 순차적으로 실행합니다:")
    print("  1. Quest Story - 퀘스트 진행")
    print("  2. Trade Story - 물물교환 진행")
    print("  3. Daily Story - 주간 컨텐츠 진행")
    print()
    print("종료하려면 Ctrl+C를 누르세요")
    print("=" * 70)
    print()

    # 3초 후 시작
    import time
    print("3초 후 시작합니다...")
    time.sleep(3)

    # 실행
    runner = MainRunner()
    runner.run()


if __name__ == "__main__":
    main()
