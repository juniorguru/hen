import logging
from dataclasses import dataclass
from enum import StrEnum, auto
from functools import wraps
from typing import Callable, Coroutine, Literal
from urllib.parse import urlparse

import blinker
import httpx
from githubkit import GitHub


USER_AGENT = "JuniorGuruBot (+https://junior.guru)"


logger = logging.getLogger("jg.hen.core")


on_profile = blinker.Signal()
on_avatar = blinker.Signal()


class ResultType(StrEnum):
    DONE = auto()
    RECOMMENDATION = auto()


@dataclass
class Result:
    rule: str
    type: ResultType
    message: str
    docs_url: str


@dataclass
class Context:
    profile_url: str
    username: str


@dataclass
class Summary:
    status: Literal["ok", "error"]
    results: list[Result]
    error: Exception | None = None


def with_github(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(fn)
    async def wrapper(*args, **kwargs) -> Coroutine:
        async with GitHub(user_agent=USER_AGENT) as github:
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
        context = Context(profile_url=profile_url, username=username)

        import jg.hen.rules  # noqa

        response = await github.rest.users.async_get_by_username(username)
        user = response.parsed_data
        results.extend(collect_results(await on_profile.send_async(context, user=user)))

        response = await http.get(user.avatar_url)
        results.extend(
            collect_results(await on_avatar.send_async(context, avatar=response))
        )
    except Exception as error:
        if raise_on_error:
            raise
        return Summary(status="error", results=results, error=error)
    return Summary(status="ok", results=results)


def collect_results(
    raw_results: list[tuple[Callable, Result | None]],
) -> list[Result]:
    return [result for _, result in raw_results if result]


def rule(signal: blinker.Signal, docs_url: str) -> Callable:
    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @wraps(fn)
        async def wrapper(*args, **kwargs) -> Result | None:
            try:
                result = await fn(*args, **kwargs)
                if result is None:
                    raise NotImplementedError(
                        f"Rule {fn.__name__!r} returned no result"
                    )
                return Result(
                    rule=fn.__name__,
                    type=result[0],
                    message=result[1],
                    docs_url=docs_url,
                )
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
