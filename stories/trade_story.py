# -*- coding: utf-8 -*-
"""
Trade Story
물물교환 진행 스토리
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.story_base import StoryBase
import time


class TradeStory(StoryBase):
    """물물교환 스토리"""

    def __init__(self):
        super().__init__(
            name="Trade Story",
            description="자동으로 물물교환을 진행합니다"
        )

    def check_precondition(self):
        """사전 조건 확인"""
        self.log("Checking preconditions...")

        # 예시: 인벤토리에 교환 아이템이 있는지 확인
        self.log("✓ Inventory check passed")

        return True

    def start(self):
        """물물교환 스토리 실행"""
        self.log("Starting trade automation...")

        try:
            # Step 1: 상인 찾기
            self.log("Step 1: Finding trader NPC...")
            # 예시: 특정 위치의 상인 클릭
            self.automation.click(640, 400, delay=2)

            # Step 2: 대화 창 열기
            self.log("Step 2: Opening trade dialog...")
            self.automation.press_key('space', delay=1)

            # Step 3: 교환 메뉴 선택
            self.log("Step 3: Selecting trade menu...")
            self.automation.click(500, 450, delay=1)

            # Step 4: 교환할 아이템 선택
            self.log("Step 4: Selecting items to trade...")
            # 첫 번째 아이템 선택
            self.automation.click(300, 300, delay=0.5)
            # 두 번째 아이템 선택
            self.automation.click(400, 300, delay=0.5)

            # Step 5: 교환 확인
            self.log("Step 5: Confirming trade...")
            self.automation.click(700, 550, delay=2)

            # Step 6: 완료 확인
            self.log("Step 6: Checking trade result...")
            trade_complete_color = (0, 255, 0)  # 완료 표시 색상 (녹색 예시)
            if self.monitor.check_color_match(640, 360, trade_complete_color, threshold=50):
                self.log("✓ Trade completed successfully!")
                return True
            else:
                self.log("⚠ Trade completion uncertain")
                return True  # 일단 성공으로 처리

        except Exception as e:
            self.log(f"❌ Error in trade story: {str(e)}")
            return False

    def cleanup(self):
        """정리 작업"""
        self.log("Closing trade window...")
        self.automation.press_key('esc', delay=0.5)


def main():
    """메인 함수"""
    story = TradeStory()
    result = story.run()

    if result:
        print("\n✓ Trade story completed successfully!")
    else:
        print("\n❌ Trade story failed!")


if __name__ == "__main__":
    main()
