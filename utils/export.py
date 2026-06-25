import csv
import os
import re
from datetime import datetime

INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')


def save_to_csv(data: list, keyword: str):
    if not data:
        print("저장할 데이터가 없습니다.")
        return

    safe_keyword = INVALID_FILENAME_CHARS.sub("_", keyword).strip() or "result"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"leads_{safe_keyword}_{timestamp}.csv"
    filepath = os.path.join(os.path.dirname(__file__), "..", "output", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    fieldnames = ["출처", "회사명", "직무", "이메일", "URL"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"\n저장 완료: {os.path.abspath(filepath)} (총 {len(data)}건)")
