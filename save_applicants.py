import pandas as pd
df = pd.read_csv("C:/Users/스토어링크/Desktop/global/output/일본상표출원_2026_화장품.csv", encoding="utf-8-sig")
df["검색대상"] = df["출원인"].where(df["출원인"].fillna("") != "", df["권리자"])
unique = df[["검색대상","상표명","출원일자"]].drop_duplicates(subset=["검색대상"]).fillna("")
unique.to_csv("C:/Users/스토어링크/Desktop/global/출원인목록.csv", index=False, encoding="utf-8-sig")
print(f"저장완료: {len(unique)}개")
