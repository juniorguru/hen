from typing import Any

from jg.hen.models import RepositoryContext
from jg.hen.signals import insight, on_repos


@insight(on_repos)
async def contributions(contexts: list[RepositoryContext]) -> list[dict[str, Any]]:
    external_contexts = [context for context in contexts if context.is_external]
    return [
        {
            "name": context.repo.full_name,
            "source_url": context.repo.html_url,
            "description": context.repo.description,
            "priority": context.pin_index,
            "stars": context.repo.stargazers_count,
        }
        for context in sorted(external_contexts, key=lambda c: c.pin_index)
    ]
