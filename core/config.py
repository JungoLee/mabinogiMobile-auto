# -*- coding: utf-8 -*-
"""
Configuration Management
설정 관리 모듈
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .constants import (
    DEFAULT_ACTION_DELAY,
    DEFAULT_STORY_PAUSE,
    CONFIG_FILE
)
from .exceptions import ConfigurationError


@dataclass
class MonitorConfig:
    """모니터링 설정"""
    before_start: bool = True
    duration: int = 5
    scale: float = 0.9
    window_title: str = "Real-time Monitor"


@dataclass
class StoryConfig:
    """스토리 설정"""
    enabled: bool = True
    timeout: int = 300
    retry_count: int = 3


@dataclass
class AppConfig:
    """애플리케이션 전체 설정"""
    # Tesseract OCR
    tesseract_path: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    ocr_language: str = "eng"

    # Automation settings
    failsafe: bool = True
    pause_between_actions: float = DEFAULT_ACTION_DELAY
    pause_between_stories: float = DEFAULT_STORY_PAUSE

    # Story settings
    enabled_stories: List[str] = field(default_factory=list)
    story_order: List[str] = field(default_factory=list)

    # Monitor settings
    monitor: MonitorConfig = field(default_factory=MonitorConfig)

    # Story-specific configs
    stories: Dict[str, StoryConfig] = field(default_factory=dict)

    # Auto restart
    auto_restart: bool = False

    # Realtime monitor
    realtime_monitor: bool = True

    def __post_init__(self):
        """초기화 후 검증"""
        self.validate()

    def validate(self) -> None:
        """설정 값 검증"""
        if self.pause_between_actions < 0:
            raise ConfigurationError("pause_between_actions", "Must be non-negative")

        if self.pause_between_stories < 0:
            raise ConfigurationError("pause_between_stories", "Must be non-negative")

        if self.monitor.duration < 0:
            raise ConfigurationError("monitor.duration", "Must be non-negative")

        if not 0.1 <= self.monitor.scale <= 2.0:
            raise ConfigurationError("monitor.scale", "Must be between 0.1 and 2.0")

        # Tesseract 경로 검증 (경고만)
        if self.tesseract_path and not os.path.exists(self.tesseract_path):
            import warnings
            warnings.warn(f"Tesseract path not found: {self.tesseract_path}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """딕셔너리에서 설정 로드"""
        # Monitor 설정
        monitor_data = {}
        if "monitor_before_start" in data:
            monitor_data["before_start"] = data["monitor_before_start"]
        if "monitor_duration" in data:
            monitor_data["duration"] = data["monitor_duration"]
        if "monitor_scale" in data:
            monitor_data["scale"] = data["monitor_scale"]
        if "monitor_window_title" in data:
            monitor_data["window_title"] = data["monitor_window_title"]

        monitor = MonitorConfig(**monitor_data) if monitor_data else MonitorConfig()

        # Story 설정
        stories = {}
        if "stories" in data and isinstance(data["stories"], dict):
            for name, story_data in data["stories"].items():
                if isinstance(story_data, dict):
                    stories[name] = StoryConfig(**story_data)

        # 메인 설정
        return cls(
            tesseract_path=data.get("tesseract_path", cls.tesseract_path),
            ocr_language=data.get("language", cls.ocr_language),
            failsafe=data.get("failsafe", cls.failsafe),
            pause_between_actions=data.get("pause_between_actions", cls.pause_between_actions),
            pause_between_stories=data.get("pause_between_stories", cls.pause_between_stories),
            enabled_stories=data.get("enabled_stories", []),
            story_order=data.get("story_order", []),
            monitor=monitor,
            stories=stories,
            auto_restart=data.get("auto_restart", cls.auto_restart),
            realtime_monitor=data.get("realtime_monitor", cls.realtime_monitor)
        )

    @classmethod
    def from_json_file(cls, filepath: str = CONFIG_FILE) -> 'AppConfig':
        """JSON 파일에서 설정 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            import warnings
            warnings.warn(f"Config file not found: {filepath}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            raise ConfigurationError(message=f"Invalid JSON in config file: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            "tesseract_path": self.tesseract_path,
            "language": self.ocr_language,
            "failsafe": self.failsafe,
            "pause_between_actions": self.pause_between_actions,
            "pause_between_stories": self.pause_between_stories,
            "enabled_stories": self.enabled_stories,
            "story_order": self.story_order,
            "monitor_before_start": self.monitor.before_start,
            "monitor_duration": self.monitor.duration,
            "monitor_scale": self.monitor.scale,
            "monitor_window_title": self.monitor.window_title,
            "stories": {
                name: {
                    "enabled": story.enabled,
                    "timeout": story.timeout,
                    "retry_count": story.retry_count
                }
                for name, story in self.stories.items()
            },
            "auto_restart": self.auto_restart,
            "realtime_monitor": self.realtime_monitor
        }

    def save_to_file(self, filepath: str = CONFIG_FILE) -> None:
        """설정을 JSON 파일로 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


def load_config(filepath: str = CONFIG_FILE) -> AppConfig:
    """
    설정 파일 로드 (편의 함수)

    Args:
        filepath: 설정 파일 경로

    Returns:
        AppConfig 객체
    """
    return AppConfig.from_json_file(filepath)
