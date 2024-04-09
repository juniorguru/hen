from io import BytesIO

import httpx
from githubkit.rest import PublicUser, SocialAccount
from PIL import Image

from jg.hen.core import (
    ResultType,
    on_avatar_response,
    on_pinned_repos,
    on_profile,
    on_social_accounts,
    rule,
)


IDENTICON_GREY = (240, 240, 240)


@rule(
    on_avatar_response,
    "https://junior.guru/handbook/github-profile/#nastav-si-vlastni-obrazek",
)
async def has_avatar(avatar_response: httpx.Response) -> tuple[ResultType, str]:
    try:
        avatar_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Failed to fetch avatar: {e}") from e

    with Image.open(BytesIO(avatar_response.content)) as image:
        colors = image.getcolors()

    if (
        colors is not None  # has less than 256 colors
        and len(colors) <= 2  # has 2 or less colors
        and (IDENTICON_GREY in [color[1] for color in colors])  # identicon gray
    ):
        return ResultType.RECOMMENDATION, "Nastav si profilový obrázek."
    return ResultType.DONE, "Vlastní profilový obrázek máš nastavený."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_name(user: PublicUser) -> tuple[ResultType, str]:
    if user.name:
        return ResultType.DONE, f"Jméno máš vyplněné: {user.name}"
    return ResultType.RECOMMENDATION, "Doplň si jméno."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(user: PublicUser) -> tuple[ResultType, str]:
    if user.bio:
        return ResultType.DONE, "Bio máš vyplněné"
    return ResultType.RECOMMENDATION, "Doplň si bio."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(user: PublicUser) -> tuple[ResultType, str]:
    if user.location:
        return (ResultType.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return ResultType.RECOMMENDATION, "Doplň si lokaci."


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(social_accounts: list[SocialAccount]) -> tuple[ResultType, str]:
    for account in social_accounts:
        if account.provider == "linkedin":
            return ResultType.DONE, f"LinkedIn máš vyplněný: {account.url}"
    return ResultType.RECOMMENDATION, "Doplň si odkaz na svůj LinkedIn profil."


@rule(
    on_pinned_repos,
    "https://junior.guru/handbook/github-profile/#vypichni-to-cim-se-chlubis",
)
async def has_some_pinned_repos(pinned_repos: list[str]) -> tuple[ResultType, str]:
    pinned_repos_count = len(pinned_repos)
    if pinned_repos_count:
        return (
            ResultType.DONE,
            f"Máš nějaké připnuté repozitáře (celkem {pinned_repos_count})",
        )
    return (
        ResultType.RECOMMENDATION,
        "Připni si repozitáře, kterými se chceš chlubit.",
    )
