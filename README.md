# 게임 자동화 스크립트

화면을 캡처하고 특정 텍스트를 인식하여 자동으로 게임을 조작하는 Python 스크립트입니다.

## 주요 기능

- **텍스트 인식**: OCR을 사용하여 화면의 텍스트 감지
- **이미지 인식**: OpenCV로 특정 이미지 패턴 찾기
- **자동 조작**: 마우스 클릭, 키보드 입력 자동화
- **조건부 실행**: 특정 조건 충족 시 원하는 동작 실행
- **로그 기록**: 모든 동작을 시간과 함께 기록

## 필요 사항

### 1. Python 설치
Python 3.8 이상이 필요합니다.

### 2. Tesseract OCR 설치 (필수!)

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

3. **Tesseract 경로 확인**
`game_automation.py` 파일을 열어서 Tesseract 경로가 맞는지 확인:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 사용 방법

### 1. 좌표 찾기

먼저 클릭할 위치의 좌표를 찾아야 합니다:

```bash
python find_coordinates.py
```

- 게임 화면에서 클릭할 위치로 마우스를 이동
- `Space` 키를 눌러 좌표 저장
- `q` 키로 종료
- 저장된 좌표를 메모

### 2. 설정 수정

`game_automation.py` 파일을 열어서 `run_automation()` 메서드를 수정:

```python
def run_automation(self, check_interval=2):
    self.running = True
    self.log("===== 게임 자동화 시작 =====")

    try:
        while self.running:
            # 예시: "시작" 텍스트를 찾아서 (250, 200) 위치 클릭
            if self.find_text_in_region("시작", region=(100, 100, 400, 300)):
                self.click_at(250, 200, delay=1)

            # 예시: "확인" 텍스트 발견 시 Enter 키 입력
            elif self.find_text_in_region("확인"):
                self.press_key('enter', delay=1)

            time.sleep(check_interval)
```

### 3. 자동화 실행

```bash
python game_automation.py
```

**중단 방법:**
- 마우스를 화면 왼쪽 위 모서리로 이동
- 또는 `Ctrl + C`

## 주요 함수 사용법

### 화면 캡처
```python
# 전체 화면
screenshot = automation.capture_screen()

# 특정 영역 (x, y, width, height)
screenshot = automation.capture_screen(region=(100, 100, 400, 300))
```

### 텍스트 인식
```python
# 특정 영역에서 텍스트 찾기
if automation.find_text_in_region("시작", region=(100, 100, 400, 300)):
    print("'시작' 텍스트 발견!")
```

### 마우스 조작
```python
# 일반 클릭
automation.click_at(x=500, y=300)

# 더블 클릭
automation.click_at(x=500, y=300, clicks=2)

# 우클릭
automation.click_at(x=500, y=300, button='right')
```

### 키보드 입력
```python
# 단일 키
automation.press_key('enter')
automation.press_key('space')

# 조합키
automation.press_hotkey('ctrl', 'c')
automation.press_hotkey('alt', 'tab')

# 텍스트 입력
automation.type_text('hello world')
```

### 이미지 찾기
```python
# 화면에서 이미지 찾기
result = automation.find_image('button.png', threshold=0.8)
if result:
    x, y, w, h = result
    automation.click_at(x + w//2, y + h//2)  # 중앙 클릭
```

## 설정 파일 (config.json)

자동화 동작을 JSON 파일로 관리할 수 있습니다:

```json
{
  "actions": [
    {
      "name": "게임 시작 버튼 클릭",
      "enabled": true,
      "trigger_text": "시작",
      "trigger_region": [100, 100, 400, 300],
      "action_type": "click",
      "action_params": {
        "x": 250,
        "y": 200,
        "delay": 1
      }
    }
  ]
}
```

## 실전 예제

### 예제 1: 퀘스트 자동 수락
```python
# "퀘스트 수락" 버튼을 찾아서 클릭
if automation.find_text_in_region("퀘스트", region=(800, 600, 200, 100)):
    automation.click_at(900, 650, delay=0.5)
    automation.click_at(900, 700, delay=1)  # 확인 버튼
```

### 예제 2: 아이템 수집
```python
# "아이템 획득" 메시지 확인
if automation.find_text_in_region("획득"):
    automation.press_key('space', delay=0.5)  # 다음 진행
```

### 예제 3: 전투 자동화
```python
# 적 발견 시 스킬 사용
if automation.find_text_in_region("적"):
    automation.press_key('1', delay=0.5)  # 스킬 1
    automation.press_key('2', delay=0.5)  # 스킬 2
    automation.click_at(640, 360)  # 공격 클릭
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

## 파일 구조

```
mabinogiMobile-auto/
├── game_automation.py      # 메인 자동화 스크립트
├── find_coordinates.py     # 좌표 찾기 도구
├── config.json            # 설정 파일
├── requirements.txt       # 필요 패키지 목록
└── README.md             # 이 문서
```

## 업데이트 계획

- [ ] GUI 인터페이스 추가
- [ ] 더 많은 이미지 인식 옵션
- [ ] 설정 파일 기반 자동화
- [ ] 로그 파일 저장
- [ ] 스크린샷 자동 저장

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 문의

문제가 있거나 질문이 있으시면 이슈를 열어주세요.
