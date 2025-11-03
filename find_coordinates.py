"""
마우스 좌표 찾기 유틸리티
게임 화면에서 클릭할 위치의 좌표를 찾는데 사용합니다.
"""

import pyautogui
import time
import keyboard

print("=" * 60)
print("마우스 좌표 찾기 도구")
print("=" * 60)
print()
print("사용 방법:")
print("1. 이 프로그램이 실행되면 3초 후부터 좌표 감지가 시작됩니다")
print("2. 마우스를 원하는 위치로 이동한 후 'Space' 키를 누르세요")
print("3. 현재 마우스 위치의 좌표와 픽셀 색상이 출력됩니다")
print("4. 'q' 키를 누르면 프로그램이 종료됩니다")
print()
print("=" * 60)

time.sleep(3)
print("\n좌표 감지 시작! (종료: 'q' 키)\n")

saved_positions = []

try:
    while True:
        if keyboard.is_pressed('space'):
            # 현재 마우스 위치
            x, y = pyautogui.position()

            # 현재 위치의 픽셀 색상
            pixel_color = pyautogui.pixel(x, y)

            # 정보 출력
            print(f"좌표: ({x}, {y}) | RGB 색상: {pixel_color}")

            # 저장
            saved_positions.append((x, y, pixel_color))

            # 연속 입력 방지
            time.sleep(0.3)

        elif keyboard.is_pressed('q'):
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

print("\n" + "=" * 60)
print("저장된 좌표 목록:")
print("=" * 60)

for i, (x, y, color) in enumerate(saved_positions, 1):
    print(f"{i}. 좌표: ({x}, {y}) | RGB: {color}")

print("\n프로그램 종료")
