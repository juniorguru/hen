import json
import logging
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import StrEnum, auto
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Coroutine
from urllib.parse import urlparse

import blinker
import httpx
from githubkit import GitHub
from githubkit.exception import RequestFailed
from githubkit.rest import FullRepository


USER_AGENT = "JuniorGuruBot (+https://junior.guru)"

PINNED_REPOS_GQL = Path(__file__).with_name("pinned_repos.gql").read_text()


logger = logging.getLogger("jg.hen.core")


on_profile = blinker.Signal()
on_avatar_response = blinker.Signal()
on_social_accounts = blinker.Signal()
on_repo = blinker.Signal()
on_repos = blinker.Signal()


class Status(StrEnum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DONE = auto()


@dataclass
class Outcome:
    rule: str
    status: Status
    message: str
    docs_url: str


@dataclass
class Insight:
    name: str
    value: Any
    collect: bool = False


@dataclass
class Summary:
    username: str
    outcomes: list[Outcome]
    insights: dict[str, Any]
    error: Exception | None = None


@dataclass
class RepositoryContext:
    repo: FullRepository
    readme: str | None
    is_profile: bool
    pin: int | None


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
        import jg.hen.insights  # noqa

        response = await github.rest.users.async_get_by_username(username)
        user = response.parsed_data
        results.extend(await send(on_profile, user=user))

        response = await http.get(user.avatar_url)
        results.extend(await send(on_avatar_response, avatar_response=response))

        response = await github.rest.users.async_list_social_accounts_for_user(username)
        social_accounts = response.parsed_data
        results.extend(await send(on_social_accounts, social_accounts=social_accounts))

        data = await github.async_graphql(PINNED_REPOS_GQL, {"login": username})
        pinned_urls = [repo["url"] for repo in data["user"]["pinnedItems"]["nodes"]]

        contexts = []
        async for minimal_repo in github.paginate(
            github.rest.repos.async_list_for_user, username=username, type="owner"
        ):
            response = await github.rest.repos.async_get(username, minimal_repo.name)
            repo = response.parsed_data
            readme = None
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
                pin=get_pin(pinned_urls, repo.html_url),
            )
            results.extend(await send(on_repo, context=context))
            contexts.append(context)
        results.extend(await send(on_repos, contexts=contexts))
    except Exception as error:
        if raise_on_error:
            raise
        return create_summary(username=username, results=results, error=error)
    return create_summary(username=username, results=results)


async def send(signal: blinker.Signal, **kwargs) -> list[Outcome | Insight]:
    return collect_results(await signal.send_async(None, **kwargs))


def collect_results(
    raw_results: list[tuple[Callable, Outcome | Insight | None]],
) -> list[Outcome | Insight]:
    return [result for _, result in raw_results if result]


def get_pin(pinned_urls: list[str], repo_url: str) -> int | None:
    try:
        return pinned_urls.index(repo_url)
    except ValueError:
        return None


def create_summary(
    username: str, results: list[Outcome | Insight], error: Exception | None = None
) -> Summary:
    return Summary(
        username=username,
        outcomes=[result for result in results if isinstance(result, Outcome)],
        insights={
            result.name: result.value
            for result in results
            if isinstance(result, Insight)
        },
        error=error,
    )


def rule(signal: blinker.Signal, docs_url: str) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(sender: None, *args, **kwargs) -> Outcome | None:
            try:
                result = await fn(*args, **kwargs)
                if result is not None:
                    return Outcome(
                        rule=fn.__name__,
                        status=result[0],
                        message=result[1],
                        docs_url=docs_url,
                    )
                logger.debug(f"Rule {fn.__name__!r} returned no outcome")
            except NotImplementedError:
                logger.warning(f"Rule {fn.__name__!r} not implemented")
            return None

        signal.connect(wrapper)
        return wrapper

    return decorator


def insight(signal: blinker.Signal) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(sender: None, *args, **kwargs) -> Insight:
            try:
                value = await fn(*args, **kwargs)
                if value is None:
                    logger.debug(f"Insight {fn.__name__!r} returned no value")
            except NotImplementedError:
                logger.warning(f"Insight {fn.__name__!r} not implemented")
            return Insight(name=fn.__name__, value=value)

        signal.connect(wrapper)
        return wrapper

    return decorator


def parse_username(profile_url: str) -> str:
    parts = urlparse(profile_url)
    if not parts.netloc.endswith("github.com"):
        raise ValueError("Only GitHub profiles are supported")
    return parts.path.strip("/")


def to_json(summary: Summary) -> str:
    return json.dumps(asdict(summary), indent=2, ensure_ascii=False, default=serialize)


def serialize(obj: Any) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Exception):
        return str(obj)
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable."
    )
