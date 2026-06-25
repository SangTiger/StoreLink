import csv
import glob
import os

from utils.leveling import country_from_tel

INFO_DIR = os.path.join(os.path.dirname(__file__), "info")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

FIELDNAMES = [
    "companyName",
    "storeName",
    "contactName",
    "telInfo",
    "mailInfo",
    "addressInfo",
    "customerCenter",
    "categoryName",
    "productUrl",
]


def latest_file(pattern: str) -> str | None:
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def main():
    qoo10_path = latest_file(os.path.join(INFO_DIR, "qoo10JP_ranking_company_list_removed_*.csv"))
    if not qoo10_path:
        print("큐텐 데이터 파일을 info/ 폴더에서 찾지 못했습니다.")
        return

    print(f"큐텐 데이터: {qoo10_path}")

    seen = {"국내": set(), "일본": set(), "미확인": set()}
    rows_by_country = {"국내": [], "일본": [], "미확인": []}

    with open(qoo10_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            company = row.get("companyName", "").strip()
            if not company:
                continue
            country = country_from_tel(row.get("telInfo", ""))
            if company in seen[country]:
                continue
            seen[country].add(company)
            rows_by_country[country].append({key: row.get(key, "") for key in FIELDNAMES})

    name_map = {"국내": "큐텐_한국기업", "일본": "큐텐_일본기업", "미확인": "큐텐_국가미확인기업"}
    for country, filename in name_map.items():
        rows = rows_by_country[country]
        out_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"저장 완료: {os.path.abspath(out_path)} (총 {len(rows)}개 기업)")


if __name__ == "__main__":
    main()
