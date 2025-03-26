import logging
from pathlib import Path
from urllib.parse import urlparse

import httpx
from githubkit import GitHub
from githubkit.exception import RequestFailed

from jg.hen.clients import with_github, with_http
from jg.hen.data import DataRecorder, get_response_processor
from jg.hen.models import RepositoryContext, Summary
from jg.hen.signals import (
    load_receivers,
    on_avatar_response,
    on_profile,
    on_repo,
    on_repos,
    on_social_accounts,
    send,
)


PINNED_REPOS_GQL = Path(__file__).with_name("pinned_repos.gql").read_text()


logger = logging.getLogger("jg.hen.core")


@with_github
@with_http
async def check_profile_url(
    profile_url: str,
    github: GitHub,
    http: httpx.AsyncClient,
    raise_on_error: bool = False,
    record_data: DataRecorder | None = None,
) -> Summary:
    results = []
    username = parse_username(profile_url)
    process_response = get_response_processor(record_data)
    try:
        load_receivers(["jg.hen.rules", "jg.hen.insights"])

        response = await github.rest.users.async_get_by_username(username)
        user = await process_response(response)
        results.extend(await send(on_profile, user=user))

        response = await http.get(user.avatar_url)
        results.extend(await send(on_avatar_response, avatar_response=response))

        response = await github.rest.users.async_list_social_accounts_for_user(username)
        social_accounts = await process_response(response)
        results.extend(await send(on_social_accounts, social_accounts=social_accounts))

        data = await github.async_graphql(PINNED_REPOS_GQL, {"login": username})
        if record_data:
            await record_data(PINNED_REPOS_GQL, data)
        pinned_urls = [repo["url"] for repo in data["user"]["pinnedItems"]["nodes"]]

        contexts = []
        async for minimal_repo in github.paginate(
            github.rest.repos.async_list_for_user, username=username, type="owner"
        ):
            response = await github.rest.repos.async_get(username, minimal_repo.name)
            repo = await process_response(response)
            readme = None
            pin = get_pin(pinned_urls, repo.html_url)
            # For efficiency, ignore downloading README for archived repos
            # which are not pinned
            if pin is not None or not repo.archived:
                try:
                    response = await github.rest.repos.async_get_readme(
                        username,
                        repo.name,
                        headers={"Accept": "application/vnd.github.html+json"},
                    )
                    readme = response.text
                except RequestFailed as error:
                    if error.response.status_code != 404:
                        raise
            context = RepositoryContext(
                repo=repo,
                readme=readme,
                is_profile=repo.name == username,
                pin=pin,
            )
            results.extend(await send(on_repo, context=context))
            contexts.append(context)
        results.extend(await send(on_repos, contexts=contexts))
    except Exception as error:
        if raise_on_error:
            raise
        return Summary.create(username=username, results=results, error=error)
    return Summary.create(username=username, results=results)


def parse_username(profile_url: str) -> str:
    parts = urlparse(profile_url)
    if not parts.netloc.endswith("github.com"):
        raise ValueError("Only GitHub profiles are supported")
    return parts.path.strip("/")


def get_pin(pinned_urls: list[str], repo_url: str) -> int | None:
    try:
        return pinned_urls.index(repo_url)
    except ValueError:
        return None
