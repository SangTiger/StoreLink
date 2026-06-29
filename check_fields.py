import requests, xml.etree.ElementTree as ET

KEY = "KV8m6zJo=5H5TORD=i6A5ZS4DvoYe6tIjS=LijZJnRI="
url = f"http://plus.kipris.or.kr/openapi/rest/ForeignTradeMarkAdvencedSearchService/advancedSearch?tradeMarkClassificationCode=3&collectionValues=JP&docsCount=3&currentPage=1&accessKey={KEY}"

r = requests.get(url, timeout=20)
root = ET.fromstring(r.content.decode("utf-8", errors="replace"))

lines = []
item = root.find(".//searchResult")
if item is not None:
    for child in item:
        val = (child.text or "").encode("ascii", "replace").decode()
        lines.append(f"{child.tag}: {val}")

with open("C:/Users/스토어링크/Desktop/global/fields_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("done")
