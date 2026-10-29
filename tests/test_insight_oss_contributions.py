import pytest

from jg.hen.insights.oss_contributions import oss_contributions
from jg.hen.models import RepositoryContext


@pytest.mark.asyncio
async def test_insight_oss_contributions(context: RepositoryContext):
    context.pin_index = 2

    result = await oss_contributions(None, contexts=[], external_contexts=[context])

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
async def test_insight_oss_contributions_empty(context: RepositoryContext):
    result = await oss_contributions(None, contexts=[context], external_contexts=[])

    assert result.value == []
