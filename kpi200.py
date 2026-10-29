from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from openpyxl import Workbook


URL = "https://kr.tradingview.com/symbols/KRX-KOSPI200/components/"
OUTPUT_FILE = Path(__file__).with_name("kospi200.xlsx")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}


def get_cell_text(cell: Tag) -> str:
    text = " ".join(cell.get_text(" ", strip=True).split())
    return text.replace("−", "-")


def get_top_constituents(
    soup: BeautifulSoup,
) -> list[tuple[str, str, str, str, str]]:
    table = soup.find("table")
    if table is None:
        raise ValueError("KOSPI 200 구성종목 표를 찾지 못했습니다.")

    constituents: list[tuple[str, str, str, str, str]] = []
    for row in table.select("tr[data-rowkey^='KRX:']"):
        cells = row.find_all("td")
        symbol_links = row.select('a[href^="/symbols/KRX-"]')
        if len(cells) < 4 or len(symbol_links) < 2:
            raise ValueError("구성종목 표의 행 형식이 예상과 다릅니다.")

        row_key = row.get("data-rowkey")
        if not isinstance(row_key, str) or ":" not in row_key:
            raise ValueError("구성종목 행에서 종목코드를 찾지 못했습니다.")

        code = row_key.split(":", maxsplit=1)[1]
        name = get_cell_text(symbol_links[1])
        market_cap = get_cell_text(cells[1])
        price = get_cell_text(cells[2])
        change = get_cell_text(cells[3])
        constituents.append((code, name, market_cap, price, change))

    if not constituents:
        raise ValueError("KOSPI 200 구성종목 데이터가 없습니다.")

    return constituents


def save_to_excel(
    constituents: list[tuple[str, str, str, str, str]],
) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    if worksheet is None:
        raise RuntimeError("엑셀 워크시트를 생성하지 못했습니다.")

    worksheet.title = "KOSPI200"
    worksheet.append(["종목코드", "종목명", "시가총액", "현재가", "등락률"])
    for constituent in constituents:
        worksheet.append(list(constituent))
    workbook.save(OUTPUT_FILE)


def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    constituents = get_top_constituents(soup)

    save_to_excel(constituents)
    print("종목코드 | 종목명 | 시가총액 | 현재가 | 등락률")
    for code, name, market_cap, price, change in constituents:
        print(f"{code} | {name} | {market_cap} | {price} | {change}")
    print(f"\n엑셀 파일 저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
