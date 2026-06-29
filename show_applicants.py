import pandas as pd
df = pd.read_csv("C:/Users/스토어링크/Desktop/global/output/일본상표출원_2026_화장품.csv", encoding="utf-8-sig")
applicants = df[["출원인","권리자","상표명","출원일자"]].fillna("")
applicants["검색대상"] = applicants["출원인"].where(applicants["출원인"] != "", applicants["권리자"])
unique = applicants.drop_duplicates(subset=["검색대상"])
unique.to_csv("C:/Users/스토어링크/Desktop/global/applicants_list.txt", index=False, encoding="utf-8-sig")
print(f"총 {len(df)}건 / 고유 출원인: {len(unique)}개")
for _, r in unique.iterrows():
    print(f"  [{r['출원일자']}] {r['검색대상']} / 상표: {r['상표명'][:30] if r['상표명'] else '-'}")
