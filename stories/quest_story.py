# -*- coding: utf-8 -*-
"""
Quest Story
퀘스트 진행 스토리
"""

import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.story_base import StoryBase
import time


class QuestStory(StoryBase):
    """퀘스트 진행 스토리"""

    def __init__(self):
        super().__init__(
            name="Quest Story",
            description="자동으로 퀘스트를 수락하고 진행합니다"
        )

    def check_precondition(self):
        """사전 조건 확인"""
        self.log("Checking preconditions...")

        # 예시: 게임 화면이 열려있는지 확인
        # 실제로는 특정 이미지나 색상으로 확인
        self.log("✓ Game window is active")

        return True

    def start(self):
        """퀘스트 스토리 실행"""
        self.log("Starting quest automation...")

        try:
            # Step 1: 퀘스트 창 열기
            self.log("Step 1: Opening quest window...")
            # 예시: Q 키를 눌러 퀘스트 창 열기
            self.automation.press_key('q', delay=1)

            # Step 2: 퀘스트 찾기
            self.log("Step 2: Looking for available quests...")
            # 예시: 특정 위치에 퀘스트가 있는지 확인
            quest_color = (255, 200, 0)  # 퀘스트 표시 색상 (노란색 예시)
            if self.monitor.check_color_match(500, 300, quest_color):
                self.log("✓ Quest found!")

                # Step 3: 퀘스트 클릭
                self.log("Step 3: Clicking quest...")
                self.automation.click(500, 300, delay=1)

                # Step 4: 퀘스트 수락 버튼 클릭
                self.log("Step 4: Accepting quest...")
                self.automation.click(700, 500, delay=1)

                # Step 5: 퀘스트 목표 확인
                self.log("Step 5: Checking quest objective...")
                self.automation.wait(2)

                self.log("✓ Quest accepted successfully!")
                return True
            else:
                self.log("⚠ No quest available")
                return False

        except Exception as e:
            self.log(f"❌ Error in quest story: {str(e)}")
            return False

    def cleanup(self):
        """정리 작업"""
        self.log("Closing quest window...")
        self.automation.press_key('esc', delay=0.5)


def main():
    """메인 함수"""
    story = QuestStory()
    result = story.run()

    if result:
        print("\n✓ Quest story completed successfully!")
    else:
        print("\n❌ Quest story failed!")


if __name__ == "__main__":
    main()
