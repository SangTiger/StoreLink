"""큐텐 한국기업 ↔ 사람인/파우더룸 자동 매칭 (Claude API 활용).

이미 aliases.csv에 있는 항목은 제외하고 나머지를 Claude에게 보내
매칭 후보를 제안받아 output/alias_suggestions.csv에 저장한다.
확신도 '높음' 항목은 aliases.csv에 자동 추가된다.
"""

import csv
import json
import os
import re
import time
import glob

import anthropic

from utils.leveling import country_from_tel

INFO_DIR = os.path.join(os.path.dirname(__file__), "info")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
ALIASES_PATH = os.path.join(OUTPUT_DIR, "aliases.csv")


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


def load_already_matched() -> set:
    matched = set()
    try:
        with open(ALIASES_PATH, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = row.get("큐텐_회사명", "").strip()
                if name:
                    matched.add(name)
    except FileNotFoundError:
        pass
    return matched


def append_to_aliases(rows: list):
    existing = load_already_matched()
    added = 0
    with open(ALIASES_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for r in rows:
            if r["큐텐_회사명"] not in existing:
                writer.writerow([r["큐텐_회사명"], r["매칭_회사명"], r["출처"]])
                existing.add(r["큐텐_회사명"])
                added += 1
    return added


def ask_claude(client, batch: list, saramin: list, powderroom: list) -> list:
    qoo10_lines = "\n".join(
        f"- {r['companyName']} | 브랜드: {extract_brand(r.get('storeName', ''))}"
        for r in batch
    )
    saramin_lines = "\n".join(f"- {n}" for n in saramin)
    powderroom_lines = "\n".join(f"- {n}" for n in powderroom)

    prompt = f"""아래는 큐텐 한국 기업 목록입니다. 법인명과 브랜드명을 보고,
사람인 또는 파우더룸 목록에서 동일한 회사/브랜드를 찾아주세요.

【큐텐 기업 목록】 (법인명 | 큐텐 브랜드명)
{qoo10_lines}

【사람인 회사명 목록】
{saramin_lines}

【파우더룸 브랜드명 목록】
{powderroom_lines}

규칙:
1. 확실히 동일한 회사/브랜드일 때만 매칭하세요 (불확실하면 제외)
2. 영문 법인명 ↔ 한글 브랜드명도 같은 회사면 매칭하세요
   예) COSRX inc. → 코스알엑스, MANYO FACTORY → 마녀공장
3. 한 큐텐 기업이 사람인+파우더룸 양쪽에 있으면 두 줄로 각각 출력하세요
4. 확신도: '높음'(거의 확실) / '보통'(그럴 것 같음)

JSON 배열만 반환 (다른 텍스트 없이):
[
  {{"큐텐_회사명": "...", "매칭_회사명": "...", "출처": "사람인", "확신도": "높음"}},
  {{"큐텐_회사명": "...", "매칭_회사명": "...", "출처": "파우더룸", "확신도": "보통"}}
]
매칭 없으면 []"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()

    # JSON 블록 추출 (마크다운 코드블록 대응)
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group())


def main():
    # 큐텐 한국기업 로드
    qoo10_path = sorted(
        glob.glob(os.path.join(INFO_DIR, "qoo10JP_ranking_company_list_removed_*.csv"))
    )[-1]

    with open(qoo10_path, newline="", encoding="utf-8-sig") as f:
        qoo10_rows = [
            r for r in csv.DictReader(f)
            if country_from_tel(r.get("telInfo", "")) == "국내"
        ]

    seen = set()
    qoo10_unique = []
    for r in qoo10_rows:
        name = r["companyName"].strip()
        if name and name not in seen:
            seen.add(name)
            qoo10_unique.append(r)

    already_matched = load_already_matched()
    unmatched = [r for r in qoo10_unique if r["companyName"].strip() not in already_matched]

    saramin = sorted(set(load_column(os.path.join(OUTPUT_DIR, "leads_사람인.csv"), "회사명")))
    powderroom = sorted(set(load_column(os.path.join(OUTPUT_DIR, "leads_파우더룸.csv"), "회사명")))

    print(f"큐텐 한국기업 전체: {len(qoo10_unique)}개 / 이미 매칭됨: {len(already_matched)}개")
    print(f"미매칭 처리 대상: {len(unmatched)}개")
    print(f"사람인 후보: {len(saramin)}개 / 파우더룸 후보: {len(powderroom)}개\n")

    client = anthropic.Anthropic()

    all_suggestions = []
    BATCH_SIZE = 25
    total_batches = (len(unmatched) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(unmatched), BATCH_SIZE):
        batch = unmatched[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"[{batch_num}/{total_batches}] {len(batch)}개 처리 중...", end=" ", flush=True)

        try:
            results = ask_claude(client, batch, saramin, powderroom)
            all_suggestions.extend(results)
            high = sum(1 for r in results if r.get("확신도") == "높음")
            print(f"제안 {len(results)}개 (높음: {high}개)")
        except Exception as e:
            print(f"오류: {e}")

        if batch_num < total_batches:
            time.sleep(0.5)

    # 전체 제안 저장
    suggestions_path = os.path.join(OUTPUT_DIR, "alias_suggestions.csv")
    with open(suggestions_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["큐텐_회사명", "매칭_회사명", "출처", "확신도"])
        writer.writeheader()
        writer.writerows(all_suggestions)

    high_conf = [r for r in all_suggestions if r.get("확신도") == "높음"]
    mid_conf = [r for r in all_suggestions if r.get("확신도") == "보통"]

    print(f"\n{'='*50}")
    print(f"전체 제안: {len(all_suggestions)}개")
    print(f"  높음: {len(high_conf)}개 → aliases.csv에 자동 추가")
    print(f"  보통: {len(mid_conf)}개 → alias_suggestions.csv 확인 후 수동 추가")

    # 높은 확신도만 자동 추가
    if high_conf:
        added = append_to_aliases(high_conf)
        print(f"\naliases.csv에 {added}개 추가 완료")
        print("→ build_brand_db.py 재실행하면 brand_db에 반영됩니다")

    print(f"\n전체 제안 저장: {suggestions_path}")


if __name__ == "__main__":
    main()
