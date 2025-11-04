# -*- coding: utf-8 -*-
"""
Click Tracker - 클릭 좌표 추적
자동화 클릭을 모니터에 실시간으로 표시하기 위한 공유 데이터
"""

import threading
import time

class ClickTracker:
    """싱글톤 클릭 트래커"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.clicks = []  # [(x, y, timestamp), ...]
                    cls._instance.click_duration = 3.0  # 표시 시간
        return cls._instance

    def add_click(self, x, y):
        """클릭 추가"""
        with self._lock:
            self.clicks.append((x, y, time.time()))
            # 오래된 클릭 제거
            current_time = time.time()
            self.clicks = [(cx, cy, ct) for cx, cy, ct in self.clicks
                          if current_time - ct < self.click_duration]

    def get_recent_clicks(self):
        """최근 클릭 목록 반환"""
        with self._lock:
            current_time = time.time()
            # 오래된 클릭 제거
            self.clicks = [(cx, cy, ct) for cx, cy, ct in self.clicks
                          if current_time - ct < self.click_duration]
            return list(self.clicks)

    def clear(self):
        """모든 클릭 기록 삭제"""
        with self._lock:
            self.clicks.clear()
