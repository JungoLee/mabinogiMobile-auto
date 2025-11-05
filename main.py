# -*- coding: utf-8 -*-
"""
Real-time Screen Monitor
실시간 화면 모니터링 프로그램 (자동화 없음)
"""

import sys
import os
import time

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('color')  # ANSI 색상 활성화

from core.realtime_monitor import RealtimeMonitor


def main():
    """진입점"""
    print("=" * 80)
    print(" " * 20 + "Real-time Screen Monitor")
    print("=" * 80)
    print()
    print("  📺 실시간 화면 모니터링 프로그램")
    print()
    print("  ✓ 실시간 마우스 위치 및 색상 표시")
    print("  ✓ Detection Area (게임 컨트롤 영역) 표시")
    print("  ✓ 화면 크기: 90% (조정 가능)")
    print()
    print("  종료: Q 키 또는 Ctrl+C")
    print("=" * 80)
    print()

    # 3초 후 시작
    print("3초 후 시작합니다...")
    for i in range(3, 0, -1):
        print(f"  {i}...", end="\r")
        time.sleep(1)
    print("  시작!     ")
    print()

    # 모니터링 실행 (scale=0.9 = 90%)
    monitor = RealtimeMonitor(window_title="Detection Area Monitor", scale=0.9)
    try:
        monitor.start()
        print("\n✓ 모니터링 시작됨")
        print("화면 모니터링만 실행합니다. (Q 키 또는 Ctrl+C로 종료)\n")

        # 모니터가 종료될 때까지 대기
        while monitor.running:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n⚠ 사용자에 의해 중단됨")
    finally:
        monitor.stop()
        print("모니터링 종료")


if __name__ == "__main__":
    main()
