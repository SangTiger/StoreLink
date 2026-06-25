from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.common import create_driver, random_sleep

RANKING_URL = "https://www.powderroom.co.kr/ranking"


def crawl_powderroom(max_scrolls: int = 20) -> list:
    """파우더룸 랭킹 페이지에서 브랜드/제품 목록을 수집한다. (연락처 정보는 제공되지 않음)"""
    driver = create_driver(headless=True)
    results = []
    seen = set()

    try:
        driver.get(RANKING_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )
        random_sleep(1.5, 2.5)

        for i in range(max_scrolls):
            cards = driver.find_elements(By.CSS_SELECTOR, ".product-item")
            before_count = len(seen)

            for card in cards:
                try:
                    brand = card.find_element(By.CSS_SELECTOR, ".brand-name").text.strip()
                    product = card.find_element(By.CSS_SELECTOR, ".product-name").text.strip()
                except NoSuchElementException:
                    continue

                key = (brand, product)
                if not brand or key in seen:
                    continue
                seen.add(key)

                link = ""
                try:
                    anchor = card.find_element(By.XPATH, "./ancestor::a[1]")
                    link = anchor.get_attribute("href")
                except NoSuchElementException:
                    pass

                results.append(
                    {
                        "출처": "파우더룸",
                        "회사명": brand,
                        "직무": product,
                        "이메일": "",
                        "URL": link,
                    }
                )

            print(f"  [파우더룸] 스크롤 {i + 1}회 (누적 {len(seen)}건)")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_sleep(1.5, 2.5)

            if len(seen) == before_count:
                print("  [파우더룸] 더 이상 새로운 항목이 없어 종료합니다.")
                break

    finally:
        driver.quit()

    return results
