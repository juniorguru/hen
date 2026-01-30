from typing import Any

from jg.hen.models import RepositoryContext
from jg.hen.readme import extract_image_urls, extract_title
from jg.hen.signals import insight, on_repos


@insight(on_repos)
async def projects(contexts: list[RepositoryContext]) -> list[dict[str, Any]]:
    projects = []
    for context in contexts:
        projects.append(
            {
                "name": context.repo.full_name,
                "title": await extract_title(context.readme),
                "source_url": context.repo.html_url,
                "demo_url": context.demo_url,
                "description": context.repo.description,
                "priority": context.pin_index,
                "start_on": context.repo.created_at.date(),
                "end_on": context.repo.pushed_at.date(),
                "topics": context.repo.topics,
                "languages": (
                    list(context.languages.keys()) if context.languages else []
                ),
                "readme_image_urls": await extract_image_urls(context.readme),
            }
        )
    return projects
