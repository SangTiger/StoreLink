import csv
import re

SUFFIX_PATTERN = re.compile(
    r"(주식회사|유한회사|\(주\)|㈜|株式会社|有限会社|co\.,?\s*ltd\.?|co\.,?\s*ltd|inc\.?|corp\.?|k\.k\.?)",
    re.IGNORECASE,
)
NON_ALNUM_PATTERN = re.compile(r"[^0-9a-zA-Z가-힣]+")


def normalize_company_name(name: str) -> str:
    if not name:
        return ""
    cleaned = SUFFIX_PATTERN.sub("", name)
    cleaned = NON_ALNUM_PATTERN.sub("", cleaned)
    return cleaned.strip().lower()


def country_from_tel(tel: str) -> str:
    if not tel:
        return "미확인"
    if tel.startswith("+81"):
        return "일본"
    if tel.startswith("+82"):
        return "국내"
    return "미확인"


def load_qoo10(filepath: str) -> list:
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            company = row.get("companyName", "").strip()
            if not company:
                continue
            rows.append(
                {
                    "channel": "큐텐",
                    "company_name": company,
                    "country": country_from_tel(row.get("telInfo", "")),
                    "tel": row.get("telInfo", ""),
                    "mail": row.get("mailInfo", ""),
                    "url": row.get("productUrl", ""),
                    "category": row.get("categoryName", ""),
                }
            )
    return rows


CHANNEL_COUNTRY = {
    "사람인": "국내",
    "파우더룸": "국내",
    "원티드": "국내",
    "앳코스메": "일본",
    "LIPS": "일본",
}


def load_leads(filepaths) -> list:
    """리드 채널(사람인, 파우더룸, 앳코스메, LIPS 등) CSV 파일들을 읽어 합친다.

    filepaths: 단일 경로(str) 또는 경로 리스트.
    국가는 파일 내 '출처' 컬럼 값을 기준으로 CHANNEL_COUNTRY에서 결정한다.
    동일 채널을 여러 번 크롤링한 파일이 섞여 있어도 회사명 기준으로
    중복이 제거되므로 그냥 전부 합쳐서 읽으면 된다.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    rows = []
    for filepath in filepaths:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                company = row.get("회사명", "").strip()
                if not company:
                    continue
                channel = row.get("출처", "")
                rows.append(
                    {
                        "channel": channel,
                        "company_name": company,
                        "country": CHANNEL_COUNTRY.get(channel, "미확인"),
                        "tel": "",
                        "mail": row.get("이메일", ""),
                        "url": row.get("URL", ""),
                        "category": row.get("직무", ""),
                    }
                )
    return rows


def level_from_channel_count(channel_count: int) -> str:
    if channel_count >= 3:
        return "S"
    if channel_count == 2:
        return "A"
    return "B"


def build_brand_db(*row_groups: list) -> list:
    brands = {}
    for rows in row_groups:
        for row in rows:
            key = normalize_company_name(row["company_name"])
            if not key:
                continue
            brand = brands.setdefault(
                key,
                {
                    "회사명": row["company_name"],
                    "국가": row["country"],
                    "채널목록": set(),
                    "연락처": set(),
                    "이메일": set(),
                    "URL": set(),
                },
            )
            brand["채널목록"].add(row["channel"])
            if row["country"] != "미확인":
                brand["국가"] = row["country"]
            if row["tel"]:
                brand["연락처"].add(row["tel"])
            if row["mail"]:
                brand["이메일"].add(row["mail"])
            if row["url"]:
                brand["URL"].add(row["url"])

    result = []
    for brand in brands.values():
        result.append(
            {
                "회사명": brand["회사명"],
                "국가": brand["국가"],
                "레벨": level_from_channel_count(len(brand["채널목록"])),
                "채널목록": ", ".join(sorted(brand["채널목록"])),
                "연락처": ", ".join(sorted(brand["연락처"])),
                "이메일": ", ".join(sorted(brand["이메일"])),
                "URL": ", ".join(sorted(brand["URL"])),
            }
        )
    country_order = {"국내": 0, "일본": 1, "미확인": 2}
    level_order = {"S": 0, "A": 1, "B": 2}
    result.sort(
        key=lambda b: (
            country_order.get(b["국가"], 99),
            level_order.get(b["레벨"], 99),
            b["회사명"],
        )
    )
    return result
