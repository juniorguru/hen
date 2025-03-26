from pathlib import Path

import pytest
from githubkit.rest import PublicUser
from pydantic import TypeAdapter


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def user(fixtures_dir: Path) -> PublicUser:
    fixture_path = fixtures_dir / "user.json"
    fixture_json = fixture_path.read_text()
    return TypeAdapter(PublicUser).validate_json(fixture_json)
