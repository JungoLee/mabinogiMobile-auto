# -*- coding: utf-8 -*-
"""
Story Base Module
스토리 실행을 위한 베이스 클래스
"""

import sys
import datetime
from core.monitor import Monitor
from core.automation import Automation

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class StoryBase:
    """스토리 베이스 클래스"""

    def __init__(self, name, description=""):
        """
        Args:
            name: 스토리 이름
            description: 스토리 설명
        """
        self.name = name
        self.description = description
        self.monitor = Monitor()
        self.automation = Automation()
        self.status = "ready"  # ready, running, completed, failed
        self.log_enabled = True

    def log(self, message):
        """로그 출력"""
        if self.log_enabled:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # 에러 메시지 색상 처리
            if any(keyword in message for keyword in ["❌", "Error", "error", "Failed", "failed", "⚠", "Warning", "warning"]):
                # ANSI 색상 코드: 빨간색
                print(f"\033[91m[{timestamp}] [{self.name}] {message}\033[0m")
            else:
                print(f"[{timestamp}] [{self.name}] {message}")

    def start(self):
        """스토리 시작 (오버라이드 필수)"""
        raise NotImplementedError("start() method must be implemented")

    def check_precondition(self):
        """
        사전 조건 확인 (오버라이드 권장)

        Returns:
            bool: 실행 가능 여부
        """
        return True

    def cleanup(self):
        """
        정리 작업 (오버라이드 권장)
        스토리 종료 후 실행됨
        """
        pass

    def run(self):
        """스토리 실행 (메인 실행 메서드)"""
        self.log("=" * 60)
        self.log(f"Starting story: {self.name}")
        if self.description:
            self.log(f"Description: {self.description}")
        self.log("=" * 60)

        try:
            # 사전 조건 확인
            if not self.check_precondition():
                self.log("❌ Precondition check failed")
                self.status = "failed"
                return False

            # 스토리 실행
            self.status = "running"
            result = self.start()

            # 결과 처리
            if result:
                self.status = "completed"
                self.log("✓ Story completed successfully")
            else:
                self.status = "failed"
                self.log("❌ Story failed")

            return result

        except KeyboardInterrupt:
            self.log("⚠ Story interrupted by user")
            self.status = "failed"
            return False

        except Exception as e:
            self.log(f"❌ Error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status = "failed"
            return False

        finally:
            # 정리 작업
            self.cleanup()
            self.log("=" * 60)
            self.log(f"Story ended: {self.name} (Status: {self.status})")
            self.log("=" * 60)

    def wait_and_click(self, image_path, timeout=10, delay=0):
        """
        이미지를 기다렸다가 클릭

        Args:
            image_path: 찾을 이미지 경로
            timeout: 대기 시간
            delay: 클릭 후 대기 시간

        Returns:
            bool: 성공 여부
        """
        location = self.monitor.wait_for_image(image_path, timeout)
        if location:
            self.automation.click_image(location, delay)
            return True
        return False

    def wait_and_check_color(self, x, y, color, timeout=10):
        """
        색상 변화 대기

        Args:
            x, y: 확인할 좌표
            color: 목표 색상 (r, g, b)
            timeout: 대기 시간

        Returns:
            bool: 성공 여부
        """
        return self.monitor.wait_for_color(x, y, color, timeout)
