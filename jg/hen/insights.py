from typing import Any

import httpx
from githubkit.rest import PublicUser, SocialAccount
from lxml import html

from jg.hen.core import (
    RepositoryContext,
    insight,
    on_avatar_response,
    on_profile,
    on_repos,
    on_social_accounts,
)


@insight(on_profile)
async def name(user: PublicUser) -> str | None:
    return user.name


@insight(on_profile)
async def location(user: PublicUser) -> str | None:
    return user.location


@insight(on_avatar_response)
async def avatar_url(avatar_response: httpx.Response) -> str:
    return str(avatar_response.url)


@insight(on_social_accounts)
async def linkedin_url(social_accounts: list[SocialAccount]) -> str | None:
    for account in social_accounts:
        if account.provider == "linkedin":
            return account.url


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
                "priority": context.pin,
                "start_at": context.repo.created_at,
                "end_at": context.repo.pushed_at,
                "topics": context.repo.topics,
            }
        )
    return projects


def parse_readme(readme: str | None) -> dict[str, Any | None]:
    html_tree = html.fromstring(readme or "")
    try:
        title = html_tree.cssselect("h1, h2")[0].text_content().strip()
    except IndexError:
        title = None
    return dict(title=title)
