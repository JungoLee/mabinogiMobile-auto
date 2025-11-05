# Assets Folder

이 폴더에는 이미지 인식을 위한 템플릿 이미지 파일들을 저장합니다.

## 필요한 이미지 파일들

### Daily Scenario Story
- **images/UI/game_start.png** - 초기 게임 시작 버튼 이미지
- **images/UI/game_start_yellow.png** - 캐릭터 선택 후 노란색 게임 시작 버튼 이미지
- **images/system/character_choice_coins.png** - 캐릭터의 은동전 재화 영역 이미지

## 이미지 캡처 방법

1. 게임 화면에서 해당 버튼/영역을 스크린샷으로 캡처
2. 가능한 한 정확하게 해당 요소만 캡처 (주변 배경 최소화)
3. PNG 형식으로 저장
4. 이 assets 폴더에 저장

## 주의사항

- 이미지는 실제 게임 화면과 정확히 일치해야 합니다
- 해상도가 다른 경우 매칭이 안될 수 있습니다
- 매칭 신뢰도(confidence)는 코드에서 조정 가능합니다 (기본: 0.8)
