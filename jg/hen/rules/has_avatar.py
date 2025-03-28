from io import BytesIO

import httpx
from PIL import Image

from jg.hen.models import Status
from jg.hen.signals import RuleResult, on_avatar_response, rule


IDENTICON_GREY = (240, 240, 240)


@rule(
    on_avatar_response,
    "https://junior.guru/handbook/github-profile/#nastav-si-vlastni-obrazek",
)
async def has_avatar(avatar_response: httpx.Response) -> RuleResult:
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
        return (Status.ERROR, "Nastav si profilový obrázek.")
    return (Status.DONE, "Vlastní profilový obrázek máš nastavený.")
