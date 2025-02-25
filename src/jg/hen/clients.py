from functools import wraps
from typing import Callable, Coroutine

import httpx
from githubkit import GitHub


USER_AGENT = "JuniorGuruBot (+https://junior.guru)"


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
