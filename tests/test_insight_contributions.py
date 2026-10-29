import pytest

from jg.hen.insights.contributions import contributions
from jg.hen.models import RepositoryContext


@pytest.mark.asyncio
async def test_insight_contributions(context: RepositoryContext):
    context.pin_index = 2
    context.is_external = True

    result = await contributions(None, contexts=[context])

    assert result.value == [
        {
            "name": context.repo.full_name,
            "source_url": context.repo.html_url,
            "description": context.repo.description,
            "priority": 2,
            "stars": context.repo.stargazers_count,
        }
    ]


@pytest.mark.asyncio
async def test_insight_contributions_ignores_own_repos(context: RepositoryContext):
    context.pin_index = 0

    result = await contributions(None, contexts=[context])

    assert result.value == []


@pytest.mark.asyncio
async def test_insight_contributions_sorted_by_pin_index(context: RepositoryContext):
    second = context.model_copy(update={"pin_index": 4, "is_external": True})
    first = context.model_copy(update={"pin_index": 1, "is_external": True})

    result = await contributions(None, contexts=[second, first])

    assert [item["priority"] for item in result.value] == [1, 4]
