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
    heading = soup.find(["h1", "h2"])
    return heading.get_text(strip=True) if heading else None
