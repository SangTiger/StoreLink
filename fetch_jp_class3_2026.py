import requests, xml.etree.ElementTree as ET, pandas as pd, time

KEY = "KV8m6zJo=5H5TORD=i6A5ZS4DvoYe6tIjS=LijZJnRI="
BASE = "http://plus.kipris.or.kr/openapi/rest/ForeignTradeMarkAdvencedSearchService/advancedSearch"

all_records = []
seen = set()
page = 1
zero_streak = 0  # 2026 건이 0인 연속 페이지 수

while True:
    url = (
        f"{BASE}?tradeMarkClassificationCode=3"
        f"&collectionValues=JP"
        f"&docsCount=500&currentPage={page}&accessKey={KEY}"
    )
    try:
        r = requests.get(url, timeout=20)
        try:
            xml_text = r.content.decode("utf-8")
        except UnicodeDecodeError:
            xml_text = r.content.decode("euc-kr", errors="replace")
        root = ET.fromstring(xml_text)
        total = int(root.findtext(".//totalSearchCount") or 0)
        items = root.findall(".//searchResult")

        if not items:
            break

        new_2026 = 0
        for item in items:
            num = item.findtext("applicationNumber") or ""
            app_date = item.findtext("applicationDate") or ""
            if num in seen:
                continue
            seen.add(num)
            if not app_date.startswith("2026"):
                continue
            new_2026 += 1
            all_records.append({
                "출원인":   item.findtext("applicant") or "",
                "권리자":   item.findtext("rightHolder") or "",
                "상표명":   item.findtext("tradeMarkName") or "",
                "출원번호": num,
                "출원일자": app_date,
                "등록번호": item.findtext("registrationNumber") or "",
                "등록일자": item.findtext("registrationDate") or "",
                "분류코드": item.findtext("tradeMarkClassificationCode") or "",
            })

        print(f"p{page} | 2026건 {new_2026} | 누적 {len(all_records)} / 전체 {total}")

        if new_2026 == 0:
            zero_streak += 1
            if zero_streak >= 3:  # 3페이지 연속 0이면 종료
                print("2026 데이터 소진, 종료")
                break
        else:
            zero_streak = 0

        page += 1
        time.sleep(0.8)

    except Exception as e:
        print(f"p{page} 오류: {e}")
        time.sleep(3)
        page += 1

df = pd.DataFrame(all_records).drop_duplicates(subset=["출원번호"])
df = df.sort_values("출원일자", ascending=False).reset_index(drop=True)
out = "C:/Users/스토어링크/Desktop/global/output/일본상표출원_2026_화장품.csv"
df.to_csv(out, index=False, encoding="utf-8-sig")
print(f"\n완료: {len(df)}건 -> {out}")
