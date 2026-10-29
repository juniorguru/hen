import pytest

from jg.hen.insights.contributions import contributions
from jg.hen.models import RepositoryContext


@pytest.mark.asyncio
async def test_insight_contributions(context: RepositoryContext):
    context.pin_index = 2

    result = await contributions(None, contexts=[], external_contexts=[context])

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
async def test_insight_contributions_empty(context: RepositoryContext):
    result = await contributions(None, contexts=[context], external_contexts=[])

    assert result.value == []
