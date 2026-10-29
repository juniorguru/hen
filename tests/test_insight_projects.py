import pytest

from jg.hen.insights.projects import projects
from jg.hen.models import RepositoryContext


@pytest.mark.asyncio
async def test_insight_projects_ignores_external_repos(context: RepositoryContext):
    context.pin_index = 0
    context.is_external = True

    result = await projects(None, contexts=[context])

    assert result.value == []
