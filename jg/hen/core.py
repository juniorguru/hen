import logging
from dataclasses import dataclass
from enum import StrEnum, auto
from functools import wraps
from pathlib import Path
from typing import Callable, Coroutine, Literal
from urllib.parse import urlparse

import blinker
import httpx
from githubkit import GitHub
from githubkit.exception import RequestFailed


USER_AGENT = "JuniorGuruBot (+https://junior.guru)"

PINNED_REPOS_GQL = Path(__file__).with_name("pinned_repos.gql").read_text()


logger = logging.getLogger("jg.hen.core")


on_profile = blinker.Signal()
on_avatar_response = blinker.Signal()
on_social_accounts = blinker.Signal()
on_pinned_repo = blinker.Signal()
on_pinned_repos = blinker.Signal()
on_repo = blinker.Signal()
on_repos = blinker.Signal()
on_readme = blinker.Signal()
on_profile_readme = blinker.Signal()


class ResultType(StrEnum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DONE = auto()


@dataclass
class Result:
    rule: str
    type: ResultType
    message: str
    docs_url: str


@dataclass
class Summary:
    status: Literal["ok", "error"]
    results: list[Result]
    error: Exception | None = None


def with_github(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(fn)
    async def wrapper(*args, **kwargs) -> Coroutine:
        github_api_key = kwargs.pop("github_api_key", None)
        async with GitHub(github_api_key, user_agent=USER_AGENT) as github:
            return await fn(*args, github=github, **kwargs)

    return wrapper


def with_http(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(fn)
    async def wrapper(*args, **kwargs) -> Coroutine:
        async with httpx.AsyncClient(
            follow_redirects=True, headers={"User-Agent": USER_AGENT}
        ) as client:
            return await fn(*args, http=client, **kwargs)

    return wrapper


@with_github
@with_http
async def check_profile_url(
    profile_url: str,
    github: GitHub,
    http: httpx.AsyncClient,
    raise_on_error: bool = False,
) -> Summary:
    results = []
    try:
        username = parse_username(profile_url)

        import jg.hen.rules  # noqa

        response = await github.rest.users.async_get_by_username(username)
        user = response.parsed_data
        results.extend(await send(on_profile, user=user))

        response = await http.get(user.avatar_url)
        results.extend(await send(on_avatar_response, avatar_response=response))

        response = await github.rest.users.async_list_social_accounts_for_user(username)
        social_accounts = response.parsed_data
        results.extend(await send(on_social_accounts, social_accounts=social_accounts))

        data = await github.async_graphql(PINNED_REPOS_GQL, {"login": username})
        pinned_urls = {repo["url"] for repo in data["user"]["pinnedItems"]["nodes"]}

        repos = []
        pinned_repos = []
        profile_readme = None

        async for minimal_repo in github.paginate(
            github.rest.repos.async_list_for_user, username=username, type="owner"
        ):
            response = await github.rest.repos.async_get(username, minimal_repo.name)
            repo = response.parsed_data
            results.extend(await send(on_repo, repo=repo))
            repos.append(repo)
            if repo.html_url in pinned_urls:
                results.extend(await send(on_pinned_repo, pinned_repo=repo))
                pinned_repos.append(repo)

            try:
                response = await github.rest.repos.async_get_readme(
                    username,
                    repo.name,
                    headers={"Accept": "application/vnd.github.html+json"},
                )
                readme = response.text
                results.extend(await send(on_readme, readme=readme))
                if repo.name == username:
                    profile_readme = readme
            except RequestFailed as error:
                if error.response.status_code != 404:
                    raise
                results.extend(await send(on_readme, readme=None))

        results.extend(await send(on_profile_readme, readme=profile_readme))
        results.extend(await send(on_repos, repos=repos))
        results.extend(await send(on_pinned_repos, pinned_repos=pinned_repos))
    except Exception as error:
        if raise_on_error:
            raise
        return Summary(status="error", results=results, error=error)
    return Summary(status="ok", results=results)


async def send(signal: blinker.Signal, **kwargs) -> list[Result]:
    return collect_results(await signal.send_async(None, **kwargs))


def collect_results(
    raw_results: list[tuple[Callable, Result | None]],
) -> list[Result]:
    return [result for _, result in raw_results if result]


def rule(signal: blinker.Signal, docs_url: str) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(sender: None, *args, **kwargs) -> Result | None:
            try:
                result = await fn(*args, **kwargs)
                if result is not None:
                    return Result(
                        rule=fn.__name__,
                        type=result[0],
                        message=result[1],
                        docs_url=docs_url,
                    )
                logger.debug(f"Rule {fn.__name__!r} returned no result")
            except NotImplementedError:
                logger.warning(f"Rule {fn.__name__!r} not implemented")
            return None

        signal.connect(wrapper)
        return wrapper

    return decorator


def parse_username(profile_url: str) -> str:
    parts = urlparse(profile_url)
    if not parts.netloc.endswith("github.com"):
        raise ValueError("Only GitHub profiles are supported")
    return parts.path.strip("/")
