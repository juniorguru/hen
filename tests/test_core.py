import pytest

from jg.hen.core import parse_username


@pytest.mark.parametrize(
    "profile_url, expected",
    [
        pytest.param(
            "https://github.com/honzajavorek",
            "honzajavorek",
            id="standard",
        ),
        pytest.param(
            "https://www.github.com/honzajavorek",
            "honzajavorek",
            id="www",
        ),
        pytest.param(
            "http://github.com/honzajavorek",
            "honzajavorek",
            id="http",
        ),
        pytest.param(
            "https://github.com/PetrValenta92",
            "PetrValenta92",
            id="case sensitive",
        ),
    ],
)
def test_parse_username(profile_url: str, expected: str):
    assert parse_username(profile_url) == expected


@pytest.mark.parametrize("profile_url", ["https://example.com/PetrValenta92"])
def test_parse_username_raises(profile_url: str):
    with pytest.raises(ValueError):
        parse_username(profile_url)
