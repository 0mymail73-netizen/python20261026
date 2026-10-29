import time

import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://search.naver.com/search.naver"
QUERY = "반도체"
MAX_ARTICLES = 5
OUTPUT_FILE = "naver_news_articles.txt"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}


def get_news_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    for anchor in soup.select(
        "a.news_tit, a[data-heatmap-target='.tit']"
    ):
        title = anchor.get("title") or anchor.get_text(" ", strip=True)
        title = title.replace("새 창 열림", "").strip()
        url = anchor.get("href")
        if title and url and url.startswith("http") and url not in seen_urls:
            links.append((title.strip(), url))
            seen_urls.add(url)
            if len(links) >= MAX_ARTICLES:
                break

    return links


def get_article_text(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    body = None
    for selector in (
        "#dic_area",
        "#newsct_article",
        "#articleBodyContents",
        ".newsct_article",
        ".story-news",
        "#articleWrap",
        ".article_body",
        ".article-body",
        ".article_view",
        "article",
    ):
        body = soup.select_one(selector)
        if body:
            break

    if body is None:
        raise ValueError("기사 본문 영역을 찾지 못했습니다.")

    for element in body.select("script, style, nav, aside, button"):
        element.decompose()

    text = "\n".join(
        line.strip()
        for line in body.get_text("\n").splitlines()
        if line.strip()
    )
    if not text:
        raise ValueError("기사 본문이 비어 있습니다.")
    return text


def main() -> None:
    response = requests.get(
        SEARCH_URL,
        params={"where": "news", "query": QUERY},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    articles = get_news_links(response.text)
    if not articles:
        raise RuntimeError(
            "뉴스 검색 결과에서 기사 링크를 찾지 못했습니다. "
            "네이버 검색 페이지의 HTML 구조가 변경되었는지 확인하세요."
        )

    collected: list[tuple[str, str, str]] = []
    for index, (title, url) in enumerate(articles, start=1):
        time.sleep(0.5)
        try:
            text = get_article_text(url)
        except (requests.RequestException, ValueError) as error:
            print(f"[수집 실패] {title}: {error}")
            continue

        collected.append((title, url, text))
        print(f"[{index}] {title}\n{url}\n{text[:300]}\n")

    if not collected:
        raise RuntimeError(
            "기사 링크는 찾았지만 본문을 수집하지 못했습니다. "
            "언론사별 본문 선택자를 확인하세요."
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for title, url, text in collected:
            file.write(f"{title}\n{url}\n{text}\n\n")

    print(f"{len(collected)}개 기사를 {OUTPUT_FILE}에 저장했습니다.")


if __name__ == "__main__":
    main()
