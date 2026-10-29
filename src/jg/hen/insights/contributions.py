from typing import Any

from jg.hen.models import RepositoryContext
from jg.hen.signals import insight, on_repos


@insight(on_repos)
async def contributions(
    contexts: list[RepositoryContext], external_contexts: list[RepositoryContext]
) -> list[dict[str, Any]]:
    return [
        {
            "name": context.repo.full_name,
            "source_url": context.repo.html_url,
            "description": context.repo.description,
            "priority": context.pin_index,
            "stars": context.repo.stargazers_count,
        }
        for context in external_contexts
    ]
