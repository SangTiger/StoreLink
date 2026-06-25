"""큐텐 한국기업 × 사람인/파우더룸 수동 매칭 리뷰 파일 생성.

영문 브랜드명(큐텐 storeName) ↔ 한국어 이름(사람인/파우더룸)은 알고리즘으로
자동 매칭이 불가능하므로, 직접 확인할 수 있게 두 목록을 나란히 배치한다.

output/alias_review.csv:
  - 시트 앞부분: 큐텐 한국기업 196개 목록 (companyName + storeName 브랜드명)
  - 시트 뒷부분: 사람인 / 파우더룸 전체 회사명 목록 (참고용)
  매칭되는 쌍을 확인했으면 output/aliases.csv 에 직접 추가하면 빌드 시 반영된다.

output/aliases.csv 스키마:
  큐텐_회사명, 사람인_또는_파우더룸_회사명, 출처
"""

import csv
import os
import re

from utils.leveling import country_from_tel

INFO_DIR = os.path.join(os.path.dirname(__file__), "info")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def extract_brand(store: str) -> str:
    store = re.sub(r"【[^】]*】|（[^）]*）|\([^)]*\)", "", store)
    store = re.sub(
        r"(公式|official|官方|ショップ|shop|韓国|_official|-official)",
        "",
        store,
        flags=re.IGNORECASE,
    )
    store = re.sub(r"[_/|].*", "", store)
    return store.strip()


def load_column(filepath: str, col: str) -> list:
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        return [row[col].strip() for row in csv.DictReader(f) if row.get(col, "").strip()]


def main():
    import glob

    qoo10_path = sorted(
        glob.glob(os.path.join(INFO_DIR, "qoo10JP_ranking_company_list_removed_*.csv"))
    )[-1]

    with open(qoo10_path, newline="", encoding="utf-8-sig") as f:
        qoo10_rows = [
            r for r in csv.DictReader(f)
            if country_from_tel(r.get("telInfo", "")) == "국내"
        ]

    # companyName 기준 중복 제거
    seen = set()
    qoo10_unique = []
    for r in qoo10_rows:
        name = r["companyName"].strip()
        if name and name not in seen:
            seen.add(name)
            qoo10_unique.append(r)

    saramin = load_column(os.path.join(OUTPUT_DIR, "leads_사람인.csv"), "회사명")
    powderroom = load_column(os.path.join(OUTPUT_DIR, "leads_파우더룸.csv"), "회사명")

    out_path = os.path.join(OUTPUT_DIR, "alias_review.csv")

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # 섹션 1: 큐텐 한국기업 목록
        writer.writerow(["[큐텐 한국기업 목록 - 브랜드 확인 후 아래 aliases.csv에 추가]", "", ""])
        writer.writerow(["큐텐_회사명(법인명)", "브랜드명(storeName 정제)", ""])
        for r in qoo10_unique:
            brand = extract_brand(r.get("storeName", ""))
            writer.writerow([r["companyName"], brand, ""])

        writer.writerow([])

        # 섹션 2: 사람인 목록 (참고용)
        writer.writerow(["[사람인 회사명 목록 - 참고용]", "", ""])
        for n in sorted(set(saramin)):
            writer.writerow([n, "사람인", ""])

        writer.writerow([])

        # 섹션 3: 파우더룸 목록 (참고용)
        writer.writerow(["[파우더룸 브랜드명 목록 - 참고용]", "", ""])
        for n in sorted(set(powderroom)):
            writer.writerow([n, "파우더룸", ""])

    print(f"리뷰 파일 저장: {os.path.abspath(out_path)}")
    print(f"  큐텐 한국기업 {len(qoo10_unique)}개 / 사람인 {len(set(saramin))}개 / 파우더룸 {len(set(powderroom))}개")

    # aliases.csv 가 없으면 빈 템플릿 생성
    aliases_path = os.path.join(OUTPUT_DIR, "aliases.csv")
    if not os.path.exists(aliases_path):
        with open(aliases_path, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(["큐텐_회사명", "매칭_회사명", "출처"])
        print(f"aliases 템플릿 생성: {os.path.abspath(aliases_path)}")


if __name__ == "__main__":
    main()

