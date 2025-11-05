# -*- coding: utf-8 -*-
"""
Custom Exceptions
커스텀 예외 클래스들
"""


class AutomationError(Exception):
    """Base exception for all automation errors"""
    pass


class ImageNotFoundError(AutomationError):
    """Raised when an image template is not found on screen"""

    def __init__(self, image_path, message="Image not found on screen"):
        self.image_path = image_path
        self.message = f"{message}: {image_path}"
        super().__init__(self.message)


class ConfigurationError(AutomationError):
    """Raised when configuration is invalid or missing"""

    def __init__(self, config_key=None, message="Invalid configuration"):
        self.config_key = config_key
        if config_key:
            self.message = f"{message} for key: {config_key}"
        else:
            self.message = message
        super().__init__(self.message)


class StoryExecutionError(AutomationError):
    """Raised when story execution fails"""

    def __init__(self, story_name, step=None, message="Story execution failed"):
        self.story_name = story_name
        self.step = step
        if step:
            self.message = f"{message} - Story: {story_name}, Step: {step}"
        else:
            self.message = f"{message} - Story: {story_name}"
        super().__init__(self.message)


class PreconditionFailedError(StoryExecutionError):
    """Raised when story precondition check fails"""

    def __init__(self, story_name, reason=None):
        message = f"Precondition failed for story: {story_name}"
        if reason:
            message += f" - Reason: {reason}"
        super().__init__(story_name, message=message)


class TemplateLoadError(AutomationError):
    """Raised when template image cannot be loaded"""

    def __init__(self, template_path, message="Failed to load template"):
        self.template_path = template_path
        self.message = f"{message}: {template_path}"
        super().__init__(self.message)


class DetectionAreaError(AutomationError):
    """Raised when detection area is not set or invalid"""

    def __init__(self, message="Detection area not configured"):
        super().__init__(message)


class CoordinateOutOfBoundsError(AutomationError):
    """Raised when coordinates are out of screen bounds"""

    def __init__(self, x, y, screen_width=None, screen_height=None):
        if screen_width and screen_height:
            message = f"Coordinates ({x}, {y}) out of bounds (screen: {screen_width}x{screen_height})"
        else:
            message = f"Coordinates ({x}, {y}) out of bounds"
        super().__init__(message)
