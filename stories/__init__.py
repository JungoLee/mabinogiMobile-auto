# -*- coding: utf-8 -*-
"""
Stories Package
"""

import sys
import os

# 프로젝트 루트 경로 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 스토리 임포트
try:
    from stories.quest_story import QuestStory
    from stories.trade_story import TradeStory
    from stories.daily_story import DailyStory

    __all__ = ['QuestStory', 'TradeStory', 'DailyStory']
except ImportError as e:
    print(f"Warning: Could not import stories: {e}")
    __all__ = []
