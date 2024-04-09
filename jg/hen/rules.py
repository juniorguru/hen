from io import BytesIO

import httpx
from githubkit.rest import PublicUser
from PIL import Image

from jg.hen.core import Context, ResultType, on_avatar, on_profile, rule


IDENTICON_GREY = (240, 240, 240)


@rule(
    on_avatar,
    "https://junior.guru/handbook/github-profile/#nastav-si-vlastni-obrazek",
)
async def has_avatar(
    context: Context, avatar: httpx.Response
) -> tuple[ResultType, str]:
    try:
        avatar.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Failed to fetch avatar: {e}") from e

    with Image.open(BytesIO(avatar.content)) as image:
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
async def has_name(context: Context, user: PublicUser) -> tuple[ResultType, str]:
    if user.name:
        return ResultType.DONE, f"Jméno máš vyplněné: {user.name}"
    return ResultType.RECOMMENDATION, "Doplň si jméno."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(context: Context, user: PublicUser) -> tuple[ResultType, str]:
    if user.bio:
        return ResultType.DONE, "Bio máš vyplněné"
    return ResultType.RECOMMENDATION, "Doplň si bio."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(context: Context, user: PublicUser) -> tuple[ResultType, str]:
    if user.location:
        return (ResultType.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return ResultType.RECOMMENDATION, "Doplň si lokaci."
