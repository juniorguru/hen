from typing import Any

from lxml import html

from jg.hen.models import RepositoryContext
from jg.hen.signals import insight, on_repos


@insight(on_repos)
async def projects(contexts: list[RepositoryContext]) -> list[dict[str, Any]]:
    projects = []
    for context in contexts:
        parsed_readme = parse_readme(context.readme)
        projects.append(
            {
                "name": context.repo.full_name,
                "title": parsed_readme["title"],
                "source_url": context.repo.html_url,
                "live_url": context.repo.homepage or None,
                "description": context.repo.description,
                "priority": context.pin_index,
                "start_on": context.repo.created_at.date(),
                "end_on": context.repo.pushed_at.date(),
                "topics": context.repo.topics,
                "languages": (
                    list(context.languages.keys()) if context.languages else []
                ),
            }
        )
    return projects


def parse_readme(readme: str | None) -> dict[str, Any | None]:
    if not readme:
        return dict(title=None)
    html_tree = html.fromstring(readme)
    try:
        title = html_tree.cssselect("h1, h2")[0].text_content().strip()
    except IndexError:
        title = None
    return dict(title=title)
