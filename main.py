from concurrent.futures import ThreadPoolExecutor, as_completed

from crawler.saramin import crawl_saramin
from crawler.wanted import crawl_wanted
from utils.export import save_to_csv


def main():
    keyword = input("검색 키워드를 입력하세요: ").strip()
    if not keyword:
        print("키워드를 입력해야 합니다.")
        return

    print(f"\n'{keyword}' 키워드로 사람인 / 원티드 동시 검색을 시작합니다...\n")

    tasks = {
        "사람인": crawl_saramin,
        "원티드": crawl_wanted,
    }

    all_results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(func, keyword): name for name, func in tasks.items()}

        for future in as_completed(futures):
            name = futures[future]
            try:
                site_results = future.result()
                print(f"\n[{name}] 검색 완료: {len(site_results)}건 수집")
                all_results.extend(site_results)
            except Exception as e:
                print(f"\n[{name}] 수집 중 오류 발생: {e}")

    print(f"\n총 {len(all_results)}건 수집 완료")

    if all_results:
        save_to_csv(all_results, keyword)
    else:
        print("수집된 데이터가 없습니다.")


if __name__ == "__main__":
    main()
