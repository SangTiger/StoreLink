from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.common import create_driver, extract_emails_from_page, random_sleep

LIST_URL = "https://www.saramin.co.kr/zf_user/search/recruit"


def crawl_saramin(keyword: str, max_pages: int = 5) -> list:
    """사람인에서 키워드로 채용공고를 검색해 리드 목록을 반환한다."""
    driver = create_driver()
    results = []

    try:
        for page in range(1, max_pages + 1):
            url = f"{LIST_URL}?searchType=search&searchword={keyword}&recruitPage={page}"
            driver.get(url)
            random_sleep(1.5, 3.0)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".item_recruit"))
                )
            except TimeoutException:
                print(f"  [사람인] {page}페이지: 더 이상 결과가 없어 종료합니다.")
                break

            cards = driver.find_elements(By.CSS_SELECTOR, ".item_recruit")
            if not cards:
                break

            page_items = []
            for card in cards:
                try:
                    company = card.find_element(By.CSS_SELECTOR, ".corp_name a").text.strip()
                    title_el = card.find_element(By.CSS_SELECTOR, ".job_tit a")
                    title = title_el.text.strip()
                    link = title_el.get_attribute("href")
                    if company and title and link:
                        page_items.append((company, title, link))
                except NoSuchElementException:
                    continue

            for company, title, link in page_items:
                email = _extract_email_from_detail(driver, link)
                results.append(
                    {
                        "출처": "사람인",
                        "회사명": company,
                        "직무": title,
                        "이메일": email,
                        "URL": link,
                    }
                )

            print(f"  [사람인] {page}페이지 완료 (누적 {len(results)}건)")
            random_sleep(1.0, 2.0)

    finally:
        driver.quit()

    return results


def _extract_email_from_detail(driver, link: str) -> str:
    """채용 상세 페이지를 새 탭으로 열어 본문에서 이메일을 추출한다."""
    main_window = driver.current_window_handle
    driver.execute_script("window.open(arguments[0]);", link)
    driver.switch_to.window(driver.window_handles[-1])

    email = ""
    try:
        random_sleep(1.0, 2.0)
        emails = extract_emails_from_page(driver)
        emails = [e for e in emails if not e.lower().endswith("@saramin.co.kr")]
        email = emails[0] if emails else ""
    except Exception:
        pass
    finally:
        driver.close()
        driver.switch_to.window(main_window)

    return email
