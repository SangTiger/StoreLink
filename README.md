# Lead Crawler

사람인, 원티드에서 키워드 기반으로 리드를 수집하는 크롤러

## 폴더 구조
```
lead_crawler/
├── main.py              # 실행 진입점
├── requirements.txt     # 패키지 목록
├── crawler/
│   ├── saramin.py       # 사람인 크롤러
│   └── wanted.py        # 원티드 크롤러
├── utils/
│   └── export.py        # CSV 저장
└── output/              # 수집 결과 CSV 저장 폴더 (자동 생성)
```

## 설치 방법
```bash
pip install -r requirements.txt
```

## 실행 방법
```bash
python main.py
```
→ 키워드 입력 (예: 일본 이커머스 / Qoo10 담당자 / 라쿠텐 MD)
→ output 폴더에 CSV 자동 저장

## 추천 키워드
- 일본 이커머스
- Qoo10 담당자
- 라쿠텐 MD
- 해외 이커머스 마케팅
- 일본 마케팅
