# 마비노기 모바일 자동화 프레임워크

스토리 기반 게임 자동화 프레임워크입니다. 모니터링을 통해 게임 상태를 확인하고, 정의된 스토리들을 순차적으로 실행합니다.

## 🌟 주요 기능

- **스토리 기반 실행**: 캐릭터 선택, 퀘스트, 물물교환 등을 스토리로 관리
- **모듈화 구조**: Core, Stories, Tools로 명확하게 분리
- **실시간 모니터링**: OpenCV 기반 Detection Area 실시간 표시
- **이미지 인식**: OpenCV 템플릿 매칭으로 UI 요소 감지
- **OCR 텍스트 인식**: Tesseract OCR로 게임 내 숫자/텍스트 인식
- **타입 안전성**: Python Type Hints로 코드 안정성 향상
- **중앙화된 설정**: config.json 기반 설정 관리

## 📋 필요 사항

### 1. Python 설치
Python 3.8 이상이 필요합니다.

### 2. Tesseract OCR 설치

**Windows:**
1. [Tesseract 다운로드](https://github.com/UB-Mannheim/tesseract/wiki) 페이지 방문
2. 최신 버전 설치 (tesseract-ocr-w64-setup-v5.x.x.exe)
3. 설치 시 "Additional language data" 에서 **Korean** 및 **English** 선택
4. 기본 경로에 설치: `C:\Program Files\Tesseract-OCR`

### 3. Python 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install pyautogui opencv-python pytesseract Pillow numpy keyboard
```

## 🚀 빠른 시작

1. **프로젝트 클론 또는 다운로드**
```bash
git clone <repository-url>
cd mabinogiMobile-auto
```

2. **패키지 설치**
```bash
pip install -r requirements.txt
```

3. **Daily Scenario 실행**
```bash
python daily_main.py
```

4. **모니터링만 실행**
```bash
python main.py
```

## 📂 프로젝트 구조

```
mabinogiMobile-auto/
├── core/                          # 코어 모듈 (핵심 기능)
│   ├── monitor.py                # 화면 모니터링 (캡처, 색상/이미지 인식)
│   ├── automation.py             # 마우스/키보드 자동 조작
│   ├── story_base.py             # 스토리 베이스 클래스
│   ├── realtime_monitor.py       # 실시간 OpenCV 모니터 (공통 컴포넌트)
│   ├── image_detector.py         # 이미지 탐지 모듈 (OpenCV 템플릿 매칭)
│   ├── ocr_processor.py          # OCR 처리 모듈 (Tesseract)
│   ├── config.py                 # 설정 관리 (dataclass 기반)
│   ├── constants.py              # 상수 정의
│   ├── exceptions.py             # 커스텀 예외
│   ├── logger.py                 # 중앙화된 로깅
│   └── click_tracker.py          # 클릭 추적 (싱글톤)
│
├── stories/                       # 스토리 스크립트
│   ├── daily_scenario.py         # Daily 시나리오 (캐릭터 선택, 게임 시작)
│   └── __init__.py
│
├── tools/                         # 유틸리티 도구
│   ├── find_coordinates.py       # 좌표 찾기 도구
│   ├── capture_screenshot.py     # 스크린샷 캡처 도구
│   └── test_basic.py             # 기본 기능 테스트
│
├── assets/                        # 에셋 파일
│   └── images/                   # 템플릿 이미지
│       ├── UI/                   # UI 요소 이미지
│       │   ├── game_start.png
│       │   └── game_start_yellow.png
│       └── system/               # 시스템 이미지
│           └── character_choice_coins.png
│
├── main.py                        # 실시간 모니터 전용
├── daily_main.py                  # Daily Scenario 실행 (모니터 + 자동화)
├── config.json                    # 설정 파일
├── requirements.txt               # 패키지 목록
└── README.md                      # 이 문서
```

## 🎯 주요 컴포넌트 설명

### Core 모듈

#### **RealtimeMonitor** (공통 컴포넌트)
- `core/realtime_monitor.py` - 모든 프로그램에서 재사용 가능
- OpenCV 기반 실시간 화면 모니터링
- Detection Area (우측 하단 영역) 표시
- 마우스 위치, RGB/HEX 색상, 화면 정보 표시
- 설정 가능한 스케일 (기본: 80%)
- 윈도우 제목 커스터마이징 가능

**사용 예시:**
```python
from core.realtime_monitor import RealtimeMonitor

# 모니터 생성
monitor = RealtimeMonitor(
    window_title="My Monitor",
    scale=0.9  # 90% 크기
)

# 시작
monitor.start()

# Detection Area 가져오기
area = monitor.get_detection_area()  # (x1, y1, x2, y2)

# 중지
monitor.stop()
```

#### **ImageDetector** (이미지 감지)
- OpenCV 템플릿 매칭 기반
- 단일/다중 템플릿 찾기
- 중복 제거
- 영역 제한 검색 지원

#### **OCRProcessor** (문자 인식)
- Tesseract OCR 기반
- 숫자 전용 인식 최적화
- 재화(currency) 값 추출
- 이미지 전처리 (이진화, 노이즈 제거)

#### **Config** (설정 관리)
- Dataclass 기반 타입 안전 설정
- JSON 파일 로드/저장
- 자동 검증
- 기본값 제공

### Stories

#### **DailyScenarioStory**
캐릭터 선택 및 게임 시작 자동화

**실행 단계:**
1. "게임시작" 버튼 찾기 및 클릭
2. 은동전이 가장 많은 캐릭터 선택 (OCR 기반)
3. "게임시작(노란색)" 버튼 클릭

**주요 기능:**
- 이미지 템플릿 매칭으로 버튼 찾기
- OCR로 재화 값 읽기
- 자동으로 최고 재화 캐릭터 선택

## 🔧 사용 방법

### 1. 실시간 모니터링 (모니터만)

```bash
python main.py
```

**기능:**
- Detection Area 실시간 표시
- 마우스 좌표 및 색상 정보
- Q 키로 종료

**스케일 조정:**
[main.py](main.py:45)에서 `scale` 값 변경:
```python
monitor = RealtimeMonitor(window_title="Detection Area Monitor", scale=0.9)  # 90%
```

### 2. Daily Scenario 자동화 (모니터 + 자동화)

```bash
python daily_main.py
```

**기능:**
- 실시간 모니터 표시
- 캐릭터 선택 자동화
- 게임 시작 자동화

**스케일 조정:**
[daily_main.py](daily_main.py:35-38)에서 설정:
```python
self.realtime_monitor = RealtimeMonitor(
    window_title="Daily Scenario - Detection Area",
    scale=0.9  # 여기서 크기 조정 (0.1 ~ 2.0)
)
```

### 3. 좌표 찾기

게임에서 클릭할 위치의 좌표를 찾습니다:

```bash
python tools/find_coordinates.py
```

- 마우스를 원하는 위치로 이동
- `Space` 키로 좌표 저장
- `q` 키로 종료

### 4. 스크린샷 캡처

```bash
python tools/capture_screenshot.py
```

- `S` - 전체 화면 캡처
- `F` - 영역 지정 캡처
- `Q` - 종료

## ⚙️ 설정 파일 (config.json)

```json
{
  "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
  "language": "eng",
  "failsafe": true,
  "pause_between_actions": 0.5,
  "pause_between_stories": 3,

  "monitor_before_start": true,
  "monitor_duration": 5,
  "monitor_scale": 0.9,

  "enabled_stories": [],
  "story_order": [],
  "auto_restart": false,
  "realtime_monitor": true
}
```

**주요 설정:**
- `tesseract_path`: Tesseract OCR 실행 파일 경로
- `pause_between_actions`: 액션 간 대기 시간 (초)
- `monitor_scale`: 모니터 화면 크기 (0.1 ~ 2.0)
- `realtime_monitor`: 실시간 모니터 사용 여부

## 🛠️ 새 스토리 만들기

1. `stories/` 폴더에 새 파일 생성
2. `StoryBase` 상속:

```python
from typing import Optional, Tuple
from core.story_base import StoryBase

class MyStory(StoryBase):
    def __init__(self):
        super().__init__("My Story")
        self.detection_area: Optional[Tuple[int, int, int, int]] = None

    def set_detection_area(self, area: Tuple[int, int, int, int]) -> None:
        """Detection Area 설정"""
        self.detection_area = area

    def check_precondition(self) -> bool:
        """시작 전 조건 확인"""
        return True

    def start(self) -> bool:
        """메인 로직"""
        self.log("Starting my story...")

        # 이미지 찾기
        pos = self.image_detector.find_image_in_area(
            "assets/images/my_button.png",
            area=self.detection_area
        )

        if pos:
            # 클릭
            self.automation.click(pos[0], pos[1], delay=1)

        return True
```

## 📚 Core 모듈 API

### Monitor

```python
from core.monitor import Monitor

monitor = Monitor()

# 화면 캡처
screenshot = monitor.capture()

# 픽셀 색상
color = monitor.get_pixel_color(100, 200)

# 색상 매칭
is_match = monitor.check_color_match(100, 200, (255, 0, 0), threshold=30)

# 이미지 찾기
location = monitor.find_image_on_screen('button.png', confidence=0.8)

# 대기
location = monitor.wait_for_image('button.png', timeout=10)
```

### Automation

```python
from core.automation import Automation

automation = Automation()

# 클릭
automation.click(100, 200, delay=0.5)
automation.double_click(100, 200)
automation.right_click(100, 200)

# 마우스 이동
automation.move_to(100, 200, duration=0.5)

# 키보드
automation.press_key('enter', delay=1)
automation.hotkey('ctrl', 'c')
automation.type_text('hello')

# 스크롤
automation.scroll(10)  # 양수: 위, 음수: 아래

# 대기
automation.wait(2)
```

### ImageDetector

```python
from core.image_detector import ImageDetector

detector = ImageDetector()

# 영역 내 이미지 찾기
pos = detector.find_image_in_area(
    'button.png',
    area=(100, 100, 500, 500),
    confidence=0.8
)

# 템플릿 로드
template = detector.load_template('icon.png')

# 화면 캡처
screen = detector.capture_screen(area=(0, 0, 1920, 1080))

# 템플릿 찾기
result = detector.find_template(screen, template, confidence=0.8)
```

### OCRProcessor

```python
from core.ocr_processor import OCRProcessor

ocr = OCRProcessor()

# 숫자 추출
value = ocr.extract_digits(image)

# 텍스트 추출
text = ocr.extract_text(image, language='kor+eng')

# 재화 값 찾기
currencies = ocr.find_currency_values(screen, template)
# [(100, 250, 350), (200, 450, 350), ...]
```

## 🔍 리팩토링 개선 사항

### ✅ 완료된 개선
1. **코드 중복 제거** (~1,500줄 감소)
   - 9개의 중복 모니터 파일 삭제
   - `RealtimeMonitor` 컴포넌트화

2. **모듈화 및 추상화**
   - `ImageDetector` 분리
   - `OCRProcessor` 분리
   - 재사용 가능한 컴포넌트

3. **타입 안전성**
   - 모든 함수에 Type Hints 추가
   - Optional, Tuple, List 등 명시

4. **설정 관리**
   - Dataclass 기반 `AppConfig`
   - 자동 검증 및 기본값

5. **예외 처리**
   - 커스텀 예외 클래스
   - 명확한 에러 메시지

6. **중앙화된 로깅**
   - `core/logger.py`
   - 컬러 로그, 파일 저장 지원

### 🎯 코드 품질
- **Before**: ~3,100줄 (중복 1,500줄)
- **After**: ~1,600줄 (중복 제거)
- **개선율**: ~48% 코드 감소

## ⚠️ 주의사항

**법적 주의사항:**
- 게임 이용약관을 반드시 확인하세요
- 자동화 프로그램 사용이 금지된 게임도 있습니다
- 계정 정지 위험이 있을 수 있습니다
- **교육 목적으로만 사용하세요**

**안전 기능:**
- `pyautogui.FAILSAFE = True`: 마우스를 모서리로 이동하면 중단
- 언제든지 `Ctrl + C`로 중단 가능
- Q 키로 모니터 종료

## 🐛 문제 해결

### Tesseract를 찾을 수 없다는 오류
```
TesseractNotFoundError: tesseract is not installed
```
**해결:** Tesseract OCR 설치 및 경로 확인

### 한글이 인식되지 않음
**해결:** Tesseract 설치 시 Korean language data 포함

### OCR 정확도가 낮음
**해결:**
- 이미지 전처리 개선
- 캡처 영역 정확히 지정
- confidence threshold 조정

### 자동화가 너무 빠름
**해결:** `config.json`에서 `pause_between_actions` 증가

## 📄 라이선스

MIT License

## 🤝 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 📧 문의

문제가 있거나 질문이 있으시면 이슈를 열어주세요.
