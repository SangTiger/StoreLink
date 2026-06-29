import requests, xml.etree.ElementTree as ET

KEY = "KV8m6zJo=5H5TORD=i6A5ZS4DvoYe6tIjS=LijZJnRI="
BASE = "http://plus.kipris.or.kr/openapi/rest/ForeignTradeMarkAdvencedSearchService/advancedSearch"

def get_page(page):
    url = f"{BASE}?tradeMarkClassificationCode=3&collectionValues=JP&docsCount=500&currentPage={page}&accessKey={KEY}"
    r = requests.get(url, timeout=20)
    root = ET.fromstring(r.content.decode("utf-8", errors="replace"))
    total = root.findtext(".//totalSearchCount")
    items = root.findall(".//searchResult")
    nums = [i.findtext("applicationNumber") for i in items]
    return total, nums

total1, nums1 = get_page(1)
total2, nums2 = get_page(2)

print(f"전체: {total1}건")
print(f"1페이지 첫번호: {nums1[0] if nums1 else 'none'}")
print(f"2페이지 첫번호: {nums2[0] if nums2 else 'none'}")
print(f"페이징 작동: {nums1[0] != nums2[0] if nums1 and nums2 else False}")
print(f"1p/2p 중복: {len(set(nums1) & set(nums2))}건")
