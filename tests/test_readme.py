from pathlib import Path

import pytest

from jg.hen.readme import extract_image_urls


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
