import csv
import glob
import os
import re
from datetime import datetime

from utils.leveling import build_brand_db, load_aliases, load_leads, load_qoo10

INFO_DIR = os.path.join(os.path.dirname(__file__), "info")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _next_version_path(output_dir: str) -> str:
    """기존 brand_db_v{major}.{minor}.csv 파일을 스캔해 다음 마이너 버전 파일명 반환."""
    pattern = re.compile(r"brand_db_v(\d+)\.(\d+)\.csv$")
    max_major, max_minor = 1, -1
    for f in glob.glob(os.path.join(output_dir, "brand_db_v*.csv")):
        m = pattern.search(os.path.basename(f))
        if m:
            mj, mn = int(m.group(1)), int(m.group(2))
            if (mj, mn) > (max_major, max_minor):
                max_major, max_minor = mj, mn
    next_minor = max_minor + 1
    return f"brand_db_v{max_major}.{next_minor}.csv"


def latest_file(pattern: str) -> str | None:
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def main():
    qoo10_path = latest_file(os.path.join(INFO_DIR, "qoo10JP_ranking_company_list_removed_*.csv"))
    # 국내 채널(사람인, 파우더룸 등)은 크롤링 시점마다 파일이 따로 생기므로
    # leads_*.csv 전부를 합쳐서 읽는다.
    lead_paths = sorted(glob.glob(os.path.join(OUTPUT_DIR, "leads_*.csv")))

    if not qoo10_path:
        print("큐텐 데이터 파일을 info/ 폴더에서 찾지 못했습니다.")
        return
    if not lead_paths:
        print("사람인/파우더룸 리드 파일을 output/ 폴더에서 찾지 못했습니다.")
        return

    print(f"큐텐 데이터: {qoo10_path}")
    print(f"리드 데이터: {len(lead_paths)}개 파일")
    for path in lead_paths:
        print(f"  - {path}")

    aliases_path = os.path.join(OUTPUT_DIR, "aliases.csv")
    aliases = load_aliases(aliases_path)
    if aliases:
        print(f"별칭 매핑 {len(aliases)}건 로드: {aliases_path}")

    qoo10_rows = load_qoo10(qoo10_path)
    lead_rows = load_leads(lead_paths)
    brands = build_brand_db(qoo10_rows, lead_rows, aliases=aliases)

    level_counts = {"S": 0, "A": 0, "B": 0}
    for brand in brands:
        level_counts[brand["레벨"]] += 1
    print(f"\n레벨별 브랜드 수: S={level_counts['S']}, A={level_counts['A']}, B={level_counts['B']}")

    out_path = os.path.join(OUTPUT_DIR, _next_version_path(OUTPUT_DIR))
    fieldnames = ["국가", "레벨", "회사명", "연락처", "이메일", "채널목록", "URL"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(brands)

    print(f"\n저장 완료: {os.path.abspath(out_path)} (총 {len(brands)}건)")


if __name__ == "__main__":
    main()
