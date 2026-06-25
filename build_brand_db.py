import csv
import glob
import os
from datetime import datetime

from utils.leveling import build_brand_db, load_leads, load_qoo10

INFO_DIR = os.path.join(os.path.dirname(__file__), "info")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def latest_file(pattern: str) -> str | None:
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def main():
    qoo10_path = latest_file(os.path.join(INFO_DIR, "qoo10JP_ranking_company_list_removed_*.csv"))
    leads_path = latest_file(os.path.join(OUTPUT_DIR, "leads_*.csv"))

    if not qoo10_path:
        print("큐텐 데이터 파일을 info/ 폴더에서 찾지 못했습니다.")
        return
    if not leads_path:
        print("사람인/원티드 리드 파일을 output/ 폴더에서 찾지 못했습니다.")
        return

    print(f"큐텐 데이터: {qoo10_path}")
    print(f"리드 데이터: {leads_path}")

    qoo10_rows = load_qoo10(qoo10_path)
    lead_rows = load_leads(leads_path)
    brands = build_brand_db(qoo10_rows, lead_rows)

    level_counts = {"S": 0, "A": 0, "B": 0}
    for brand in brands:
        level_counts[brand["레벨"]] += 1
    print(f"\n레벨별 브랜드 수: S={level_counts['S']}, A={level_counts['A']}, B={level_counts['B']}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUTPUT_DIR, f"brand_db_{timestamp}.csv")
    fieldnames = ["회사명", "국가", "레벨", "채널목록", "연락처", "이메일", "URL"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(brands)

    print(f"\n저장 완료: {os.path.abspath(out_path)} (총 {len(brands)}건)")


if __name__ == "__main__":
    main()
