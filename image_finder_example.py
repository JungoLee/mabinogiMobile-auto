# -*- coding: utf-8 -*-
"""
이미지 찾기 예제
특정 이미지를 화면에서 찾고 위치를 표시합니다
"""

import sys
import cv2
import numpy as np
import pyautogui

if sys.platform == 'win32':
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_image_on_screen(template_path, threshold=0.8):
    """
    화면에서 특정 이미지를 찾습니다

    Args:
        template_path: 찾을 이미지 파일 경로
        threshold: 매칭 임계값 (0.0 ~ 1.0, 높을수록 정확)

    Returns:
        찾은 위치 리스트 [(x, y, width, height), ...]
    """
    # 화면 캡처
    screenshot = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 찾을 이미지 로드
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ 이미지를 찾을 수 없습니다: {template_path}")
        return []

    # 템플릿 크기
    h, w = template.shape[:2]

    # 템플릿 매칭
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    # 임계값 이상인 위치 찾기
    locations = np.where(result >= threshold)

    # 중복 제거 및 결과 정리
    matches = []
    for pt in zip(*locations[::-1]):
        x, y = pt
        # 중복 체크 (가까운 위치는 하나로 합침)
        is_duplicate = False
        for match in matches:
            if abs(match[0] - x) < w/2 and abs(match[1] - y) < h/2:
                is_duplicate = True
                break

        if not is_duplicate:
            matches.append((x, y, w, h))

    return matches


def main():
    print("=" * 70)
    print("이미지 찾기 예제")
    print("=" * 70)
    print()
    print("사용법:")
    print("1. 찾고 싶은 이미지를 스크린샷으로 저장")
    print("2. 이 프로그램에 이미지 경로 입력")
    print("3. 화면에서 해당 이미지를 찾아 표시")
    print()

    # 예제: 특정 이미지 찾기
    template_path = input("찾을 이미지 경로를 입력하세요 (예: button.png): ").strip()

    if not template_path:
        print("이미지 경로가 입력되지 않았습니다.")
        return

    print(f"\n'{template_path}' 이미지를 화면에서 찾는 중...")

    # 이미지 찾기
    matches = find_image_on_screen(template_path, threshold=0.8)

    if matches:
        print(f"\n✓ {len(matches)}개의 매칭 발견!")

        # 화면 캡처 및 결과 표시
        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 찾은 위치에 박스 그리기
        for i, (x, y, w, h) in enumerate(matches):
            print(f"  [{i+1}] 위치: ({x}, {y}), 크기: {w}x{h}")

            # 녹색 박스 그리기
            cv2.rectangle(screen, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 번호 표시
            cv2.putText(screen, f"#{i+1}", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 화면 크기 조정 (50%)
        height, width = screen.shape[:2]
        screen = cv2.resize(screen, (width // 2, height // 2))

        # 결과 표시
        cv2.imshow('Image Search Result - [Q] to quit', screen)
        print("\n윈도우가 열렸습니다. [Q] 키를 눌러 종료하세요.")

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

        cv2.destroyAllWindows()

    else:
        print("\n❌ 이미지를 찾지 못했습니다.")
        print("  - 임계값을 낮춰보세요 (현재: 0.8)")
        print("  - 이미지가 정확히 일치하는지 확인하세요")


def example_pyautogui():
    """PyAutoGUI를 사용한 간단한 방법"""
    print("\n" + "=" * 70)
    print("PyAutoGUI 방법 (더 간단함)")
    print("=" * 70)

    template_path = input("찾을 이미지 경로: ").strip()

    if not template_path:
        return

    try:
        # PyAutoGUI로 이미지 찾기
        location = pyautogui.locateOnScreen(template_path, confidence=0.8)

        if location:
            print(f"\n✓ 이미지 발견!")
            print(f"  위치: ({location.left}, {location.top})")
            print(f"  크기: {location.width}x{location.height}")
            print(f"  중심점: {pyautogui.center(location)}")
        else:
            print("\n❌ 이미지를 찾지 못했습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    try:
        main()

        # PyAutoGUI 방법도 시도할지 물어보기
        print("\n" + "=" * 70)
        choice = input("PyAutoGUI 방법도 시도하시겠습니까? (y/n): ").strip().lower()
        if choice == 'y':
            example_pyautogui()

    except KeyboardInterrupt:
        print("\n\n종료되었습니다.")
