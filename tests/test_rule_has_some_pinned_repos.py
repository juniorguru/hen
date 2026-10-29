import pytest

from jg.hen.models import RepositoryContext, Status
from jg.hen.rules.has_some_pinned_repos import has_some_pinned_repos


@pytest.mark.asyncio
async def test_rule_has_some_pinned_repos_none(context: RepositoryContext):
    context.pin_index = None

    result = await has_some_pinned_repos(None, contexts=[context])

    assert result
    assert result.status == Status.ERROR


@pytest.mark.asyncio
async def test_rule_has_some_pinned_repos_own(context: RepositoryContext):
    context.pin_index = 0

    result = await has_some_pinned_repos(None, contexts=[context])

    assert result
    assert result.status == Status.DONE
    assert "celkem 1" in result.message


@pytest.mark.asyncio
async def test_rule_has_some_pinned_repos_only_external(context: RepositoryContext):
    context.pin_index = 0
    context.is_external = True

    result = await has_some_pinned_repos(None, contexts=[context])

    assert result
    assert result.status == Status.DONE
    assert "celkem 1" in result.message


@pytest.mark.asyncio
async def test_rule_has_some_pinned_repos_own_and_external(
    context: RepositoryContext,
):
    own_context = context.model_copy(update={"pin_index": 0})
    external_context = context.model_copy(update={"pin_index": 1, "is_external": True})

    result = await has_some_pinned_repos(None, contexts=[own_context, external_context])

    assert result
    assert result.status == Status.DONE
    assert "celkem 2" in result.message
