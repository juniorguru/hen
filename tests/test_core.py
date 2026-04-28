import pytest

from jg.hen.core import get_pin_index, is_external_repo, parse_username


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


@pytest.mark.parametrize(
    "repo_slug, pins_index, expected",
    [
        ("pepa/project", ["pepa/project"], 0),
        ("pepa/project", ["pepa/project", "pepa/other"], 0),
        ("pepa/other", ["pepa/project", "pepa/other"], 1),
        ("pepa/other", ["pepa/project"], None),
    ],
)
def test_get_pin_index(repo_slug: str, pins_index: list[str], expected: int | None):
    assert get_pin_index(repo_slug, pins_index) == expected


@pytest.mark.parametrize(
    "repo_owner, username, expected",
    [
        ("timiodon", "Ypsilonx", True),
        ("Ypsilonx", "Ypsilonx", False),
        ("ypsilonx", "Ypsilonx", False),
    ],
)
def test_is_external_repo(repo_owner: str, username: str, expected: bool):
    assert is_external_repo(repo_owner, username) is expected
