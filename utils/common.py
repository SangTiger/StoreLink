import random
import re
import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# webdriver-manager의 최초 드라이버 다운로드가 여러 스레드에서 동시에 실행되면
# 캐시 디렉터리 접근이 충돌할 수 있어 설치 단계만 직렬화한다.
_install_lock = threading.Lock()


def create_driver(headless: bool = False):
    """봇 차단 우회 옵션을 적용한 Chrome WebDriver를 생성한다."""
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1000")
    options.add_argument("--lang=ko-KR")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    # 자동화 탐지 우회
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    with _install_lock:
        driver_path = ChromeDriverManager().install()

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # navigator.webdriver 플래그 위장
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"},
        )
    except Exception:
        pass

    return driver


def random_sleep(min_sec: float = 1.0, max_sec: float = 2.5):
    """탐지 회피 및 서버 부담 완화를 위한 랜덤 딜레이."""
    time.sleep(random.uniform(min_sec, max_sec))


def extract_emails_from_text(text: str) -> list:
    return EMAIL_PATTERN.findall(text or "")


def extract_emails_from_page(driver) -> list:
    """현재 페이지(iframe 포함) 전체 텍스트에서 이메일 주소를 추출한다."""
    emails = set(extract_emails_from_text(driver.page_source))

    try:
        iframe_count = len(driver.find_elements(By.TAG_NAME, "iframe"))
    except Exception:
        iframe_count = 0

    for idx in range(iframe_count):
        try:
            driver.switch_to.frame(idx)
            emails.update(extract_emails_from_text(driver.page_source))
        except Exception:
            pass
        finally:
            driver.switch_to.default_content()

    return list(emails)
