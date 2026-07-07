from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


async def extract_image_urls(markup: str | None) -> list[str]:
    if not markup:
        return []
    soup = BeautifulSoup(markup, "html.parser")
    return [str(src) for img in soup.find_all("img") if (src := img.get("src"))]


async def extract_title(readme: str | None) -> str | None:
    if not readme:
        return None
    soup = BeautifulSoup(readme, "html.parser")
    heading = soup.find("h1")
    return heading.get_text(strip=True) if heading else None


def make_urls_absolute(
    urls: list[str], repo_owner: str, repo_name: str, branch: str
) -> list[str]:
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/"
    return [url if urlparse(url).scheme else urljoin(raw_url, url) for url in urls]
