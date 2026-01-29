from pathlib import Path

import pytest

from jg.hen.lib import extract_image_urls


@pytest.mark.asyncio
async def test_extract_image_urls_html_fixture(fixtures_dir: Path):
    readme = (fixtures_dir / "html-img-readme.md").read_text()
    urls = await extract_image_urls(readme)

    assert urls == [
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/353c0018-cdf6-48f7-befa-ead8fe27ec6f",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/30806427-0883-403f-aabe-0d7fb450d1f1",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/213f3528-635a-45a5-8ea7-46218ec0e0a2",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/3bc411f1-787f-4b81-aa77-8047389e0e34",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/b636499d-7fc2-4d9c-ac52-0acb0dc90fb6",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/27babcf9-e7ee-4bc2-99b3-4cba5d14f5e7",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/58f451c9-961d-47c2-8a5e-7e440d4a6a06",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/ebbdaa95-d931-446a-80f0-36ea3fa423b8",
        "https://github.com/PavlaBerankova/kulturmapa/assets/107038196/d305a00f-441c-4980-a83f-7863b3d48333",
    ]


@pytest.mark.asyncio
async def test_extract_image_urls_markdown_fixture(fixtures_dir: Path):
    readme = (fixtures_dir / "markdown-img-readme.md").read_text()
    urls = await extract_image_urls(readme)

    assert urls == [
        "https://user-images.githubusercontent.com/110200002/228265914-4da84468-6479-4ae8-8a82-157b1751f5b4.jpg",
        "https://user-images.githubusercontent.com/110200002/228290673-6d1cad45-0eac-4888-ac46-681d4637b7d9.png",
        "https://user-images.githubusercontent.com/110200002/228266096-01fb34af-bb49-48c0-9854-2c7409119d3e.png",
        "https://user-images.githubusercontent.com/110200002/228266107-6b022756-f009-4d23-9e0d-830ab6fe9414.png",
        "https://user-images.githubusercontent.com/110200002/228266118-90218f2d-f340-4232-8ad1-57d1dd89b5c4.png",
    ]


@pytest.mark.asyncio
async def test_extract_image_urls_mixed_fixture(fixtures_dir: Path):
    readme = (fixtures_dir / "mixed-img-readme.md").read_text()
    urls = await extract_image_urls(readme)

    assert urls == [
        "https://example.com/assets/html-image.png",
        "https://example.com/assets/another-html-image.png",
        "https://example.com/assets/markdown-image.png",
    ]
