import pandas as pd

df = pd.read_csv("C:/Users/스토어링크/Desktop/global/출원인목록.csv", encoding="utf-8-sig")

# Web search 결과 기반 한국 회사 판정
korean_map = {
    "キム  ジユン": ("한국인 개인", "김지윤", "확실"),
    "ハン  ギュリ": ("한국인 개인", "한규리", "확실"),
    "ドン  クック  ファーマシューティカル  カンパニー  リミテッド": ("동국제약", "Dongkook Pharmaceutical Co.,Ltd.", "확실"),
    "メディピンクラボ,インコーポレイテッド": ("메디핑크랩", "Medipink Lab Inc.", "확실"),
    "株式会社ビタブリッドジャパン": ("비타브리드재팬", "Vitabrid Japan (현대바이오사이언스 합작)", "확실"),
    "K-Connection株式会社": ("미확인", "K-Connection", "가능성"),
    "セオア  シーオー  エルティーディー": ("미확인", "Seoa Co., Ltd.", "가능성"),
}

rows = []
for _, r in df.iterrows():
    name = r["검색대상"]
    if name in korean_map:
        kor_name, eng_name, confidence = korean_map[name]
        rows.append({
            "출원인_일본어": name,
            "한국회사명": kor_name,
            "영문명": eng_name,
            "상표명": r["상표명"],
            "출원일자": r["출원일자"],
            "판정": confidence,
        })

result = pd.DataFrame(rows)
out = "C:/Users/스토어링크/Desktop/global/output/일본상표출원_한국기업_2026.csv"
result.to_csv(out, index=False, encoding="utf-8-sig")
with open("C:/Users/스토어링크/Desktop/global/output/korean_result.txt", "w", encoding="utf-8") as f:
    f.write(f"저장: {out}\n")
    f.write(result.to_string(index=False))
