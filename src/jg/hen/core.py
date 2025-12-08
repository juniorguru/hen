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
    on_repo_demo,
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

        logger.debug("Fetching profile data")
        response = await github.rest.users.async_get_by_username(username)
        user = await process_response(response)
        results.extend(await send(on_profile, user=user))

        logger.debug("Fetching avatar")
        response = await http.get(user.avatar_url)
        results.extend(await send(on_avatar_response, avatar_response=response))

        logger.debug("Fetching social accounts")
        response = await github.rest.users.async_list_social_accounts_for_user(username)
        social_accounts = await process_response(response)
        results.extend(
            await send(on_social_accounts, social_accounts=social_accounts, user=user)
        )

        logger.debug("Fetching a list of pinned repositories")
        data = await github.async_graphql(PINNED_REPOS_GQL, {"login": username})
        if record_data:
            await record_data(PINNED_REPOS_GQL, data)
        repo_slugs = [
            repo["nameWithOwner"] for repo in data["user"]["pinnedItems"]["nodes"]
        ]
        pins_index = list(repo_slugs)

        logger.debug("Fetching a list of owned repositories")
        async for minimal_repo in github.paginate(
            github.rest.repos.async_list_for_user, username=username, type="owner"
        ):
            repo_slugs.append(f"{username}/{minimal_repo.name}")

        contexts = []
        for repo_slug in frozenset(repo_slugs):
            logger.debug(f"Fetching details for {repo_slug}")
            repo_owner, repo_name = repo_slug.split("/")
            response = await github.rest.repos.async_get(repo_owner, repo_name)
            repo = await process_response(response)
            pin_index = get_pin_index(repo_slug, pins_index)

            readme = None
            languages = None
            demo_response = None

            if pin_index is not None or not repo.archived:
                logger.debug(f"Fetching README for {repo_slug}")
                try:
                    response = await github.rest.repos.async_get_readme(
                        repo_owner,
                        repo_name,
                        headers={"Accept": "application/vnd.github.html+json"},
                    )
                    readme = response.text
                except RequestFailed as error:
                    if error.response.status_code != 404:
                        raise

                logger.debug(f"Fetching languages for {repo_slug}")
                response = await github.rest.repos.async_list_languages(
                    repo_owner, repo_name
                )
                languages = (await process_response(response)).model_dump()

                if homepage_url := repo.homepage:
                    logger.debug(f"Fetching homepage for {repo_slug}: {homepage_url}")
                    demo_response = await http.get(
                        homepage_url, follow_redirects=True, timeout=3.0
                    )
            else:
                # For efficiency, ignore downloading additional details
                # for archived repos which are not pinned
                logger.debug(f"Skipping fetching additional details for {repo_slug}")
            context = RepositoryContext(
                username=username,
                pin_index=pin_index,
                repo=repo,
                readme=readme,
                languages=languages,
            )
            results.extend(await send(on_repo, context=context))
            contexts.append(context)

            if demo_response is not None:
                results.extend(
                    await send(
                        on_repo_demo, demo_response=demo_response, context=context
                    )
                )
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


def get_pin_index(repo_slug: str, pins_index: list[str]) -> int | None:
    try:
        return pins_index.index(repo_slug)
    except ValueError:
        return None
