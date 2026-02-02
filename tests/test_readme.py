from pathlib import Path

import pytest

from jg.hen.readme import extract_image_urls, extract_title, make_urls_absolute


@pytest.mark.asyncio
async def test_extract_image_urls_html_fixture(fixtures_dir: Path):
    readme = (fixtures_dir / "readme-html-img.md").read_text()
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
async def test_extract_image_urls_relative(fixtures_dir: Path):
    readme = (fixtures_dir / "readme-relative-link.md").read_text()
    urls = await extract_image_urls(readme)

    assert urls == [
        "./public/img/mockup.png",
        "https://camo.githubusercontent.com/c31126fcb6f4cb77220a3916a05cfaf4a86500593794dbdc2c7a6746c7f70249/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f52656163742d31382e332e312d3631444146423f6c6f676f3d7265616374",
        "https://camo.githubusercontent.com/d624bbb16055b6e962f0bc6e9a44bbf96343f3a6999eba9ab0fea22a3c77eee4/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f566974652d362e302e332d3634364346463f6c6f676f3d76697465",
        "https://camo.githubusercontent.com/5caa455d8debc46fb23abbadb45a733a937f3910a73fc875c2f7820468e1bb54/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d677265656e",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markup, expected",
    [
        ("<img alt='logo'>", []),
        ("<img src='' alt='empty'>", []),
        (None, []),
        ("", []),
    ],
)
async def test_extract_image_urls_handles_missing_sources(
    markup: str | None, expected: list[str]
):
    assert await extract_image_urls(markup) == expected


@pytest.mark.asyncio
async def test_extract_title_returns_none_for_missing_heading():
    assert await extract_title(None) is None
    assert await extract_title("") is None
    assert await extract_title("<p>No heading here</p>") is None


@pytest.mark.asyncio
async def test_extract_title_reads_primary_heading():
    readme = "<article><h1>  My Project </h1><p>Welcome</p></article>"

    assert await extract_title(readme) == "My Project"


@pytest.mark.asyncio
async def test_extract_title_falls_back_to_secondary_heading():
    readme = "<section><h2>Secondary</h2><h1>Primary</h1></section>"

    assert await extract_title(readme) == "Secondary"


@pytest.mark.parametrize(
    "urls, expected",
    [
        ([], []),
        (
            ["https://example.com/pic3.png"],
            ["https://example.com/pic3.png"],
        ),
        (
            ["./public/img/mockup.png"],
            ["https://raw.githubusercontent.com/user/repo/main/public/img/mockup.png"],
        ),
        (
            ["modern-browser-mockup.png"],
            [
                "https://raw.githubusercontent.com/user/repo/main/modern-browser-mockup.png"
            ],
        ),
        (
            ["Nu,_pogodi!_logo.png"],
            ["https://raw.githubusercontent.com/user/repo/main/Nu,_pogodi!_logo.png"],
        ),
        (
            ["docs/bottom-keyboard-clone.png"],
            [
                "https://raw.githubusercontent.com/user/repo/main/docs/bottom-keyboard-clone.png"
            ],
        ),
    ],
)
def test_make_urls_absolute(urls: list[str], expected: list[str]):
    absolute_urls = make_urls_absolute(urls, "user", "repo", "main")
    assert absolute_urls == expected
