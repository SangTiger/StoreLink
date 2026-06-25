from selenium.webdriver.common.by import By

from utils.common import create_driver, extract_emails_from_page, random_sleep

SEARCH_URL = "https://www.wanted.co.kr/search"


def crawl_wanted(keyword: str, max_scrolls: int = 15) -> list:
    """원티드에서 키워드로 채용공고를 검색해 리드 목록을 반환한다."""
    driver = create_driver()
    results = []

    try:
        url = f"{SEARCH_URL}?query={keyword}&tab=job"
        driver.get(url)
        random_sleep(2.0, 3.5)

        seen = _collect_cards_by_scroll(driver, max_scrolls)

        for idx, (link, company, title) in enumerate(seen.values(), start=1):
            email = _extract_email_from_detail(driver, link)
            results.append(
                {
                    "출처": "원티드",
                    "회사명": company,
                    "직무": title,
                    "이메일": email,
                    "URL": link,
                }
            )
            if idx % 5 == 0 or idx == len(seen):
                print(f"  [원티드] 본문 확인 {idx}/{len(seen)}건")

        print(f"  [원티드] 수집 완료 ({len(results)}건)")

    finally:
        driver.quit()

    return results


def _collect_cards_by_scroll(driver, max_scrolls: int) -> dict:
    """무한스크롤을 내리며 채용공고 카드를 누적 수집한다. key=URL, value=(URL, 회사명, 직무)."""
    seen = {}
    stale_rounds = 0

    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep(1.2, 2.2)

        before = len(seen)

        # 원티드는 프런트엔드 클래스명이 해시값이라 자주 바뀌므로,
        # 채용 상세로 연결되는 링크(/wd/) 패턴으로 카드를 식별한다.
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/wd/']")
        for a in anchors:
            href = a.get_attribute("href")
            if not href:
                continue
            href = href.split("?")[0]
            if href in seen:
                continue

            lines = [line.strip() for line in a.text.split("\n") if line.strip()]
            title = lines[0] if len(lines) >= 1 else ""
            company = lines[1] if len(lines) >= 2 else ""
            seen[href] = (href, company, title)

        print(f"  [원티드] 스크롤 {i + 1}/{max_scrolls} (누적 {len(seen)}건)")

        if len(seen) == before:
            stale_rounds += 1
        else:
            stale_rounds = 0

        if stale_rounds >= 3:
            print("  [원티드] 추가로 로드되는 공고가 없어 스크롤을 종료합니다.")
            break

    return seen


def _extract_email_from_detail(driver, link: str) -> str:
    """채용 상세 페이지를 새 탭으로 열어 본문에서 이메일을 추출한다."""
    main_window = driver.current_window_handle
    driver.execute_script("window.open(arguments[0]);", link)
    driver.switch_to.window(driver.window_handles[-1])

    email = ""
    try:
        random_sleep(1.2, 2.2)
        emails = extract_emails_from_page(driver)
        email = emails[0] if emails else ""
    except Exception:
        pass
    finally:
        driver.close()
        driver.switch_to.window(main_window)

    return email
