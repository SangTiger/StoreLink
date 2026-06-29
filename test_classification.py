import requests, xml.etree.ElementTree as ET

KEY = "KV8m6zJo=5H5TORD=i6A5ZS4DvoYe6tIjS=LijZJnRI="
BASE = "http://plus.kipris.or.kr/openapi/rest/ForeignTradeMarkAdvencedSearchService"

endpoints = [
    ("classificationSearch", "tradeMarkClassificationCode=3"),
    ("tradeMarkClassificationSearch", "tradeMarkClassificationCode=3"),
    ("goodsSearch", "tradeMarkClassificationCode=3"),
    ("niceCodeSearch", "niceCode=3"),
    ("advancedSearch", "tradeMarkClassificationCode=3"),
]

for ep, param in endpoints:
    url = f"{BASE}/{ep}?{param}&collectionValues=JP&docsCount=5&currentPage=1&accessKey={KEY}"
    try:
        r = requests.get(url, timeout=10)
        try:
            root = ET.fromstring(r.content.decode("utf-8", errors="replace"))
            total = root.findtext(".//totalSearchCount")
            code = root.findtext(".//code")
            items = len(root.findall(".//searchResult"))
            print(f"[{ep}] total={total}, code={code}, items={items}")
        except:
            print(f"[{ep}] HTTP {r.status_code} - XML 파싱 실패: {r.text[:100]}")
    except Exception as e:
        print(f"[{ep}] 오류: {e}")
