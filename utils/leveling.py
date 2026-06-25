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


def load_leads(filepath: str) -> list:
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            company = row.get("회사명", "").strip()
            if not company:
                continue
            rows.append(
                {
                    "channel": row.get("출처", ""),
                    "company_name": company,
                    "country": "국내",
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
    result.sort(key=lambda b: (b["레벨"], b["회사명"]))
    return result
