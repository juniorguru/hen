from datetime import date, datetime, timedelta
from io import BytesIO

import httpx
from githubkit.rest import PublicUser, Repository, SocialAccount
from PIL import Image

from jg.hen.core import (
    ResultType,
    on_avatar_response,
    on_pinned_repo,
    on_pinned_repos,
    on_profile,
    on_repo,
    on_social_accounts,
    rule,
)


IDENTICON_GREY = (240, 240, 240)

RECENT_REPO_THRESHOLD = timedelta(days=2 * 365)


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
        return ResultType.ERROR, "Nastav si profilový obrázek."
    return ResultType.DONE, "Vlastní profilový obrázek máš nastavený."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_name(user: PublicUser) -> tuple[ResultType, str]:
    if user.name:
        return ResultType.DONE, f"Jméno máš vyplněné: {user.name}"
    return ResultType.ERROR, "Doplň si jméno."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(user: PublicUser) -> tuple[ResultType, str]:
    if user.bio:
        return ResultType.DONE, "Bio máš vyplněné"
    return ResultType.INFO, "Doplň si bio."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(user: PublicUser) -> tuple[ResultType, str]:
    if user.location:
        return (ResultType.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return ResultType.INFO, "Doplň si lokaci."


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(social_accounts: list[SocialAccount]) -> tuple[ResultType, str]:
    for account in social_accounts:
        if account.provider == "linkedin":
            return ResultType.DONE, f"LinkedIn máš vyplněný: {account.url}"
    return ResultType.ERROR, "Doplň si odkaz na svůj LinkedIn profil."


@rule(
    on_pinned_repos,
    "https://junior.guru/handbook/github-profile/#vypichni-to-cim-se-chlubis",
)
async def has_some_pinned_repos(pinned_repos: list) -> tuple[ResultType, str]:
    pinned_repos_count = len(pinned_repos)
    if pinned_repos_count:
        return (
            ResultType.DONE,
            f"Máš nějaké připnuté repozitáře (celkem {pinned_repos_count})",
        )
    return (ResultType.ERROR, "Připni si repozitáře, kterými se chceš chlubit.")


@rule(
    on_pinned_repo,
    "https://junior.guru/handbook/github-profile/#popis-repozitare",
)
async def has_pinned_repo_with_description(
    pinned_repo: dict,
) -> tuple[ResultType, str]:
    if pinned_repo.get("description"):
        return (
            ResultType.DONE,
            f"U připnutého repozitáře {pinned_repo['url']} máš popisek.",
        )
    return (
        ResultType.ERROR,
        f"Přidej popisek k repozitáři {pinned_repo['url']}.",
    )


@rule(
    on_pinned_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_pinned_recent_repo(
    pinned_repo: dict, today: date | None = None
) -> tuple[ResultType, str]:
    today = today or date.today()
    pushed_on = datetime.fromisoformat(pinned_repo["pushedAt"]).date()
    if pushed_on > today - RECENT_REPO_THRESHOLD:
        return (
            ResultType.DONE,
            f"Na připnutém repozitáři {pinned_repo['url']} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}, což je celkem nedávno.",
        )
    return (
        ResultType.WARNING,
        f"Na repozitáři {pinned_repo['url']} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. Zvaž, zda má být takto starý kód připnutý na tvém profilu.",
    )


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_old_repo_archived(
    repo: Repository, today: date | None = None
) -> tuple[ResultType, str] | None:
    today = today or date.today()

    if repo.fork:
        return None
    if repo.pushed_at is None:
        return None

    pushed_on = repo.pushed_at.date()
    if pushed_on > today - RECENT_REPO_THRESHOLD:
        return None

    if repo.archived:
        return (
            ResultType.DONE,
            f"Repozitář {repo.url} je celkem starý (poslední změna {pushed_on:%-d.%-m.%Y}). Je dobře, že je archivovaný.",
        )
    else:
        return (
            ResultType.WARNING,
            f"Na repozitáři {repo.url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. Možná by šlo repozitář archivovat.",
        )
