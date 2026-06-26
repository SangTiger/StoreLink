# Lead Crawler & Brand DB

사람인, 원티드, 큐텐, 파우더룸, LIPS 등 다양한 채널에서 리드를 수집하고 브랜드 DB를 관리하는 툴

## 폴더 구조
```
global/
├── main.py                  # 실행 진입점
├── build_brand_db.py        # 브랜드 DB 빌드 스크립트
├── auto_alias.py            # 자동 alias 생성
├── make_alias_candidates.py # alias 후보 생성
├── split_qoo10.py           # 큐텐 데이터 분리
├── requirements.txt         # 패키지 목록
├── crawler/                 # 각 채널별 크롤러
├── utils/                   # 공통 유틸
└── output/                  # 수집 결과 저장 폴더
    ├── brand_db_v1.2.csv    # 브랜드 DB 현재 버전
    ├── aliases.csv          # 회사명 alias 목록
    └── leads_*.csv          # 채널별 리드 수집 결과
```

## brand_db 컬럼 설명
| 컬럼 | 설명 |
|------|------|
| 국가 | 국내 / 일본 / 글로벌 |
| 레벨 | S / A / B / C |
| 회사명 | 브랜드 공식 회사명 |
| 연락처 | 담당자 연락처 |
| 이메일 | 담당자 이메일 |
| 채널목록 | 수집된 채널 (사람인, 큐텐, 파우더룸 등) |
| URL | 원본 URL |
| 포인테일 진행이력 | 포인테일 계약 여부 (O/X) |
| 퍼그샵 진행이력 | 퍼그샵 계약 여부 (O/X) |
| 스토어링크 계약이력 | 스토어링크 마케팅 계약 여부 (O/빈칸) |

> `스토어링크 계약이력`: STL 마케팅 API (apia-v2.storelink.io) 기준 총 32,619건 / 고유 1,071개사 대조 (2026-06-26 기준)

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
