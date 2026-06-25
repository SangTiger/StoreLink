from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.common import create_driver, random_sleep

BASE_URL = "https://lipscosme.com"
BRANDS_URL = f"{BASE_URL}/brands"


def crawl_lips(max_pages: int = 30) -> list:
    """LIPS(lipscosme.com)의 브랜드 목록 페이지(/brands)에서 브랜드 목록을 수집한다.

    일반 요청은 봇 차단(403)에 걸려 Selenium으로 접근한다.
    """
    driver = create_driver(headless=True)
    results = []
    seen = set()

    try:
        for page in range(1, max_pages + 1):
            driver.get(f"{BRANDS_URL}?page={page}")

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".brands-list__item"))
                )
            except Exception:
                print(f"  [LIPS] {page}페이지: 더 이상 결과가 없어 종료합니다.")
                break

            random_sleep(1.0, 2.0)

            cards = driver.find_elements(By.CSS_SELECTOR, ".brands-list__item")
            if not cards:
                break

            for card in cards:
                try:
                    name_el = card.find_element(By.CSS_SELECTOR, ".brands-list__brand-name")
                    brand = name_el.text.replace("\n", " ").strip()
                    link = card.find_element(By.CSS_SELECTOR, ".brands-list__link").get_attribute("href")
                except NoSuchElementException:
                    continue

                if not brand or brand in seen:
                    continue
                seen.add(brand)

                results.append(
                    {
                        "출처": "LIPS",
                        "회사명": brand,
                        "직무": "",
                        "이메일": "",
                        "URL": link,
                    }
                )

            print(f"  [LIPS] {page}페이지 완료 (누적 {len(seen)}건)")

    finally:
        driver.quit()

    print(f"  [LIPS] 완료: 브랜드 {len(results)}건")
    return results
