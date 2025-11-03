# 마비노기 모바일 자동화 스크립트

스토리 기반 게임 자동화 프레임워크입니다. 모니터링을 통해 게임 상태를 확인하고, 정의된 스토리들을 순차적으로 실행합니다.

## 주요 기능

- **스토리 기반 실행**: 퀘스트, 물물교환, 주간컨텐츠 등을 스토리로 관리
- **모듈화 구조**: Core, Stories, Tools로 명확하게 분리
- **화면 모니터링**: 게임 상태를 실시간으로 감지
- **자동 조작**: 마우스 클릭, 키보드 입력 자동화
- **이미지/색상 인식**: 특정 이미지나 픽셀 색상으로 게임 상태 확인
- **로그 기록**: 모든 동작을 시간과 함께 기록

## 필요 사항

### 1. Python 설치
Python 3.8 이상이 필요합니다.

### 2. Tesseract OCR 설치 (선택사항 - 텍스트 인식 사용 시)

**Windows:**
1. [Tesseract 다운로드](https://github.com/UB-Mannheim/tesseract/wiki) 페이지 방문
2. 최신 버전 설치 (tesseract-ocr-w64-setup-v5.x.x.exe)
3. 설치 시 "Additional language data" 에서 **Korean** 선택
4. 기본 경로에 설치: `C:\Program Files\Tesseract-OCR`

### 3. Python 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install pyautogui opencv-python pytesseract Pillow numpy keyboard
```

## 설치 방법

1. **프로젝트 클론 또는 다운로드**
```bash
git clone <repository-url>
cd mabinogiMobile-auto
```

2. **패키지 설치**
```bash
pip install -r requirements.txt
```

3. **설정 파일 확인**
`config.json` 파일에서 실행할 스토리 설정:
```json
{
  "enabled_stories": ["quest", "trade", "daily"],
  "story_order": ["quest", "trade", "daily"],
  "pause_between_stories": 3
}
```

## 프로젝트 구조

```
mabinogiMobile-auto/
├── core/                    # 코어 모듈 (핵심 기능)
│   ├── monitor.py          # 화면 모니터링
│   ├── automation.py       # 마우스/키보드 조작
│   └── story_base.py       # 스토리 베이스 클래스
├── stories/                 # 스토리 스크립트
│   ├── quest_story.py      # 퀘스트 자동화
│   ├── trade_story.py      # 물물교환 자동화
│   └── daily_story.py      # 주간컨텐츠 자동화
├── tools/                   # 유틸리티 도구
│   ├── find_coordinates.py # 좌표 찾기 도구
│   ├── test_basic.py       # 기본 기능 테스트
│   ├── simple_monitor.py   # 간단한 모니터
│   └── realtime_monitor.py # 실시간 모니터
├── main.py                  # 메인 실행 파일
├── config.json             # 설정 파일
└── requirements.txt        # 필요 패키지 목록
```

## 사용 방법

### 1. 기본 테스트

먼저 기본 기능이 정상 작동하는지 테스트:

```bash
python tools/test_basic.py
```

### 2. 좌표 찾기

게임에서 클릭할 위치의 좌표를 찾습니다:

```bash
python tools/find_coordinates.py
```

- 게임 화면에서 클릭할 위치로 마우스 이동
- `Space` 키를 눌러 좌표 저장
- `q` 키로 종료

### 3. 스토리 수정

`stories/` 폴더의 스토리 파일을 수정하여 실제 게임에 맞게 조정:

```python
# stories/quest_story.py 예시
def start(self):
    # Step 1: 퀘스트 창 열기
    self.automation.press_key('q', delay=1)

    # Step 2: 퀘스트 클릭 (좌표는 find_coordinates.py로 찾은 값)
    self.automation.click(500, 300, delay=1)

    # Step 3: 수락 버튼 클릭
    self.automation.click(700, 500, delay=1)

    return True
```

### 4. 메인 프로그램 실행

모든 스토리를 순차적으로 실행:

```bash
python main.py
```

**중단 방법:**
- 마우스를 화면 왼쪽 위 모서리로 이동
- 또는 `Ctrl + C`

### 5. 개별 스토리 실행

특정 스토리만 테스트하고 싶을 때:

```bash
python stories/quest_story.py
python stories/trade_story.py
python stories/daily_story.py
```

## 새 스토리 만들기

1. `stories/` 폴더에 새 파일 생성 (예: `my_story.py`)
2. `StoryBase` 클래스 상속:

```python
from core.story_base import StoryBase

class MyStory(StoryBase):
    def __init__(self):
        super().__init__(
            name="My Story",
            description="내가 만든 스토리"
        )

    def check_precondition(self):
        """시작 전 조건 확인"""
        # 실행 가능한지 확인
        return True

    def start(self):
        """메인 로직"""
        # Step 1
        self.automation.click(100, 200, delay=1)

        # Step 2
        self.automation.press_key('enter', delay=1)

        # Step 3
        if self.monitor.check_color_match(500, 300, (255, 0, 0)):
            self.log("Red pixel found!")

        return True

if __name__ == "__main__":
    story = MyStory()
    story.run()
```

3. `main.py`에 스토리 추가
4. `config.json`에 스토리 이름 추가

## Core 모듈 API

### Monitor (화면 모니터링)

```python
from core.monitor import Monitor
monitor = Monitor()

# 화면 캡처
screenshot = monitor.capture()

# 특정 좌표의 픽셀 색상 확인
color = monitor.get_pixel_color(x, y)

# 색상 매칭 확인
is_match = monitor.check_color_match(x, y, (255, 0, 0), threshold=30)

# 이미지 찾기
location = monitor.find_image_on_screen('button.png', confidence=0.8)

# 이미지 나타날 때까지 대기
location = monitor.wait_for_image('button.png', timeout=10)

# 색상 나타날 때까지 대기
found = monitor.wait_for_color(x, y, (0, 255, 0), timeout=10)
```

### Automation (자동 조작)

```python
from core.automation import Automation
automation = Automation()

# 클릭
automation.click(x, y, clicks=1, button='left', delay=0)
automation.double_click(x, y)
automation.right_click(x, y)

# 마우스 이동
automation.move_to(x, y, duration=0.5)

# 드래그
automation.drag_to(x, y, duration=0.5)

# 키보드
automation.press_key('enter', delay=0)
automation.hotkey('ctrl', 'c', delay=0)
automation.type_text('hello', interval=0.1)

# 스크롤
automation.scroll(amount=10)  # 양수: 위로, 음수: 아래로

# 대기
automation.wait(seconds=2)

# 이미지 위치 클릭
automation.click_image(image_location)
```

## 문제 해결

### 1. Tesseract를 찾을 수 없다는 오류
```
TesseractNotFoundError: tesseract is not installed
```
**해결:** Tesseract OCR 설치 후 경로를 확인하세요.

### 2. 한글이 인식되지 않음
**해결:** Tesseract 설치 시 Korean language data를 함께 설치했는지 확인하세요.

### 3. 텍스트 인식 정확도가 낮음
**해결:**
- 캡처 영역을 더 정확하게 지정
- 이미지 전처리 추가 (대비 증가, 노이즈 제거)
- threshold 값 조정

### 4. 너무 빨리 실행되어 게임이 반응 못함
**해결:** `delay` 값을 증가시키거나 `check_interval` 값을 높이세요.

## 주의사항

⚠️ **법적 주의사항:**
- 게임 이용약관을 반드시 확인하세요
- 자동화 프로그램 사용이 금지된 게임도 있습니다
- 계정 정지 위험이 있을 수 있습니다
- 교육 목적으로만 사용하세요

⚠️ **안전 기능:**
- `pyautogui.FAILSAFE = True`: 마우스를 모서리로 이동하면 중단
- 언제든지 `Ctrl + C`로 중단 가능

## 설정 파일 (config.json)

```json
{
  "enabled_stories": ["quest", "trade", "daily"],
  "story_order": ["quest", "trade", "daily"],
  "monitor_before_start": true,
  "monitor_duration": 5,
  "pause_between_stories": 3,
  "auto_restart": false
}
```

- `enabled_stories`: 실행할 스토리 목록
- `story_order`: 스토리 실행 순서
- `monitor_before_start`: 시작 전 화면 모니터링 여부
- `monitor_duration`: 모니터링 시간 (초)
- `pause_between_stories`: 스토리 간 대기 시간 (초)
- `auto_restart`: 모든 스토리 완료 후 자동 재시작 여부

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 문의

문제가 있거나 질문이 있으시면 이슈를 열어주세요.
