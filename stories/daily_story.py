# -*- coding: utf-8 -*-
"""
Daily Content Story
주간 컨텐츠 진행 스토리
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.story_base import StoryBase
import time


class DailyStory(StoryBase):
    """주간 컨텐츠 스토리"""

    def __init__(self):
        super().__init__(
            name="Daily Content Story",
            description="자동으로 주간 컨텐츠를 진행합니다"
        )

    def check_precondition(self):
        """사전 조건 확인"""
        self.log("Checking preconditions...")

        # 예시: 일일 컨텐츠가 초기화되었는지 확인
        self.log("✓ Daily content is available")

        return True

    def start(self):
        """주간 컨텐츠 스토리 실행"""
        self.log("Starting daily content automation...")

        try:
            # Step 1: 컨텐츠 메뉴 열기
            self.log("Step 1: Opening daily content menu...")
            self.automation.hotkey('alt', 'd', delay=1)

            # Step 2: 첫 번째 컨텐츠 선택
            self.log("Step 2: Selecting first daily content...")
            self.automation.click(400, 250, delay=1)

            # Step 3: 입장 버튼 클릭
            self.log("Step 3: Entering content...")
            self.automation.click(640, 500, delay=3)

            # Step 4: 로딩 대기
            self.log("Step 4: Waiting for loading...")
            loading_complete = self.monitor.wait_for_color(
                640, 360,
                (100, 200, 100),  # 게임 화면 색상 예시
                timeout=15
            )

            if loading_complete:
                self.log("✓ Loading complete!")

                # Step 5: 컨텐츠 진행
                self.log("Step 5: Progressing through content...")
                self.progress_content()

                # Step 6: 보상 수령
                self.log("Step 6: Collecting rewards...")
                self.collect_rewards()

                self.log("✓ Daily content completed!")
                return True
            else:
                self.log("❌ Loading timeout")
                return False

        except Exception as e:
            self.log(f"❌ Error in daily story: {str(e)}")
            return False

    def progress_content(self):
        """컨텐츠 진행 로직"""
        self.log("Progressing content...")

        # 예시: 10번 반복 클릭
        for i in range(10):
            self.log(f"Action {i+1}/10...")
            self.automation.click(640, 360, delay=1)
            self.automation.press_key('space', delay=0.5)

    def collect_rewards(self):
        """보상 수령 로직"""
        self.log("Collecting rewards...")

        # 보상 확인 버튼 클릭
        self.automation.click(640, 450, delay=1)

        # 보상 수령 버튼 클릭
        self.automation.click(640, 500, delay=1)

    def cleanup(self):
        """정리 작업"""
        self.log("Exiting content...")
        self.automation.press_key('esc', delay=0.5)


def main():
    """메인 함수"""
    story = DailyStory()
    result = story.run()

    if result:
        print("\n✓ Daily content story completed successfully!")
    else:
        print("\n❌ Daily content story failed!")


if __name__ == "__main__":
    main()
