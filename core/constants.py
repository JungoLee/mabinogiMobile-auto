# -*- coding: utf-8 -*-
"""
Constants and Configuration Defaults
상수 및 기본 설정값
"""

# Screen monitoring constants
SCREEN_SCALE_DEFAULT = 0.8
DETECTION_AREA_TOP_RATIO = 0.5
DETECTION_AREA_BOTTOM_OFFSET = 50
MONITOR_UPDATE_INTERVAL = 0.001  # seconds

# Image detection constants
IMAGE_CONFIDENCE_THRESHOLD = 0.8
TEMPLATE_MATCH_THRESHOLD = 0.7
DUPLICATE_DETECTION_THRESHOLD_RATIO = 0.5

# OCR configuration
OCR_CONFIG_DIGITS = '--psm 7 digits'
OCR_LANGUAGE = 'eng'

# UI colors (BGR format for OpenCV)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)

# Timing constants
DEFAULT_ACTION_DELAY = 0.5
DEFAULT_CLICK_DELAY = 0.2
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_STORY_PAUSE = 3.0

# Retry configuration
MAX_RETRY_COUNT = 3
RETRY_WAIT_TIMEOUT = 30

# Logging
LOG_TIME_FORMAT = "%H:%M:%S"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Window titles
MONITOR_WINDOW_TITLE = "Real-time Monitor"
DETECTION_AREA_WINDOW_TITLE = "Detection Area"

# File paths
ASSETS_DIR = "assets"
IMAGES_DIR = "assets/images"
UI_IMAGES_DIR = "assets/images/UI"
SYSTEM_IMAGES_DIR = "assets/images/system"
CONFIG_FILE = "config.json"
