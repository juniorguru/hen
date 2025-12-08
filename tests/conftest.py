from pathlib import Path

import pytest
from githubkit.rest import FullRepository, PublicUser
from pydantic import TypeAdapter

from jg.hen.models import RepositoryContext


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def user(fixtures_dir: Path) -> PublicUser:
    fixture_path = fixtures_dir / "user.json"
    fixture_json = fixture_path.read_text()
    return TypeAdapter(PublicUser).validate_json(fixture_json)


@pytest.fixture
def repo(fixtures_dir: Path) -> FullRepository:
    fixture_path = fixtures_dir / "repo.json"
    fixture_json = fixture_path.read_text()
    return TypeAdapter(FullRepository).validate_json(fixture_json)


@pytest.fixture
def context(repo: FullRepository) -> RepositoryContext:
    return RepositoryContext(
        username="user", pin_index=None, repo=repo, readme=None, languages=None
    )
