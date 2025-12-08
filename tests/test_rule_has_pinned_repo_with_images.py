from pathlib import Path

import pytest

from jg.hen.models import RepositoryContext, Status
from jg.hen.rules.has_pinned_repo_with_images import has_pinned_repo_with_images


@pytest.mark.asyncio
async def test_rule_has_pinned_repo_with_images_not_pinned(context: RepositoryContext):
    context.pin_index = None
    context.readme = "Hello world! ![Image](image.png)"

    result = await has_pinned_repo_with_images(None, context=context)

    assert result is None


@pytest.mark.asyncio
async def test_rule_has_pinned_repo_with_images_no_readme(context: RepositoryContext):
    context.pin_index = 3
    context.readme = None

    result = await has_pinned_repo_with_images(None, context=context)

    assert result is None


@pytest.mark.asyncio
async def test_rule_has_pinned_repo_with_images_html(
    fixtures_dir: Path, context: RepositoryContext
):
    context.pin_index = 3
    context.readme = Path(fixtures_dir / "html-img-readme.md").read_text()

    result = await has_pinned_repo_with_images(None, context=context)

    assert result
    assert result.status == Status.DONE


@pytest.mark.asyncio
async def test_rule_has_pinned_repo_with_images_markdown(
    fixtures_dir: Path, context: RepositoryContext
):
    context.pin_index = 3
    context.readme = Path(fixtures_dir / "markdown-img-readme.md").read_text()

    result = await has_pinned_repo_with_images(None, context=context)

    assert result
    assert result.status == Status.DONE


@pytest.mark.asyncio
async def test_rule_has_pinned_repo_with_images_missing(context: RepositoryContext):
    context.pin_index = 3
    context.readme = "Hello world! No images here."

    result = await has_pinned_repo_with_images(None, context=context)

    assert result
    assert result.status == Status.WARNING
