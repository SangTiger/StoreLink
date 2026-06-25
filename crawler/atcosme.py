import re
import time

import requests

BASE_URL = "https://www.cosme.net"
MAIN_RANKING_URL = f"{BASE_URL}/ranking/"

CATEGORY_ID_PATTERN = re.compile(r"/categories/item/(\d+)/ranking/")
# 메인 랭킹 페이지는 <p class="brd">, 카테고리별 랭킹 페이지는 <span class="brand"> 구조를 쓴다.
ITEM_PATTERN = re.compile(
    r'class="br(?:d|and)">\s*<a href="(?:https?://www\.cosme\.net)?(/brands/\d+/)"[^>]*>([^<]+)</a>'
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9",
}


def _fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.encoding = "cp932"
    return response.text


def _discover_category_ids() -> list:
    html = _fetch(MAIN_RANKING_URL)
    return sorted(set(CATEGORY_ID_PATTERN.findall(html)))


def crawl_atcosme(max_categories: int = 80) -> list:
    """@cosme(cosme.net)의 카테고리별 랭킹 페이지에서 브랜드 목록을 수집한다."""
    results = []
    seen = set()

    category_ids = _discover_category_ids()[:max_categories]
    print(f"  [@cosme] 카테고리 {len(category_ids)}개 수집 시작")

    for idx, category_id in enumerate(category_ids, start=1):
        url = f"{BASE_URL}/categories/item/{category_id}/ranking/"
        try:
            html = _fetch(url)
        except requests.RequestException as e:
            print(f"  [@cosme] {category_id} 요청 실패: {e}")
            continue

        for brand_path, brand_name in ITEM_PATTERN.findall(html):
            brand_name = brand_name.strip()
            if not brand_name or brand_name in seen:
                continue
            seen.add(brand_name)
            results.append(
                {
                    "출처": "앳코스메",
                    "회사명": brand_name,
                    "직무": "",
                    "이메일": "",
                    "URL": f"{BASE_URL}{brand_path}",
                }
            )

        if idx % 10 == 0:
            print(f"  [@cosme] {idx}/{len(category_ids)} 카테고리 완료 (누적 브랜드 {len(seen)}건)")

        time.sleep(0.5)

    print(f"  [@cosme] 완료: 브랜드 {len(results)}건")
    return results
