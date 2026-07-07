from pathlib import Path

import pytest

from jg.hen.lib.readme import extract_image_urls, extract_title, make_urls_absolute


@pytest.mark.asyncio
async def test_extract_image_urls_reads_html_img_tags(fixtures_dir: Path):
    readme = (fixtures_dir / "readme-html-img.md").read_text()

    assert await extract_image_urls(readme) == [
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
async def test_extract_image_urls_keeps_sources_verbatim(fixtures_dir: Path):
    readme = (fixtures_dir / "readme-relative-link.md").read_text()

    assert await extract_image_urls(readme) == [
        "./public/img/mockup.png",
        "https://camo.githubusercontent.com/c31126fcb6f4cb77220a3916a05cfaf4a86500593794dbdc2c7a6746c7f70249/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f52656163742d31382e332e312d3631444146423f6c6f676f3d7265616374",
        "https://camo.githubusercontent.com/d624bbb16055b6e962f0bc6e9a44bbf96343f3a6999eba9ab0fea22a3c77eee4/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f566974652d362e302e332d3634364346463f6c6f676f3d76697465",
        "https://camo.githubusercontent.com/5caa455d8debc46fb23abbadb45a733a937f3910a73fc875c2f7820468e1bb54/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d677265656e",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markup",
    [
        pytest.param(None, id="none"),
        pytest.param("", id="empty"),
        pytest.param("<img alt='logo'>", id="img-without-src"),
        pytest.param("<img src='' alt='empty'>", id="img-with-empty-src"),
        pytest.param("<p>No images here</p>", id="no-img-tag"),
    ],
)
async def test_extract_image_urls_returns_empty(markup: str | None):
    assert await extract_image_urls(markup) == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "readme, expected",
    [
        pytest.param(None, None, id="none"),
        pytest.param("", None, id="empty"),
        pytest.param("<p>No heading here</p>", None, id="no-heading"),
        pytest.param("<h2>Only secondary</h2>", None, id="h2-without-h1"),
        pytest.param(
            "<article><h1>  My Project </h1><p>Welcome</p></article>",
            "My Project",
            id="strips-surrounding-whitespace",
        ),
        pytest.param(
            "<section><h2>Secondary</h2><h1>Primary</h1></section>",
            "Primary",
            id="prefers-h1-over-h2",
        ),
    ],
)
async def test_extract_title(readme: str | None, expected: str | None):
    assert await extract_title(readme) == expected


@pytest.mark.parametrize(
    "url, expected",
    [
        pytest.param(
            "https://example.com/pic3.png",
            "https://example.com/pic3.png",
            id="absolute-url-unchanged",
        ),
        pytest.param(
            "./public/img/mockup.png",
            "https://raw.githubusercontent.com/user/repo/main/public/img/mockup.png",
            id="dot-relative",
        ),
        pytest.param(
            "modern-browser-mockup.png",
            "https://raw.githubusercontent.com/user/repo/main/modern-browser-mockup.png",
            id="bare-filename",
        ),
        pytest.param(
            "Nu,_pogodi!_logo.png",
            "https://raw.githubusercontent.com/user/repo/main/Nu,_pogodi!_logo.png",
            id="special-characters",
        ),
        pytest.param(
            "docs/bottom-keyboard-clone.png",
            "https://raw.githubusercontent.com/user/repo/main/docs/bottom-keyboard-clone.png",
            id="subdirectory",
        ),
    ],
)
def test_make_urls_absolute(url: str, expected: str):
    assert make_urls_absolute([url], "user", "repo", "main") == [expected]


def test_make_urls_absolute_empty_list():
    assert make_urls_absolute([], "user", "repo", "main") == []
