from datetime import date, timedelta
from io import BytesIO

import httpx
from githubkit.rest import FullRepository, PublicUser, SocialAccount
from PIL import Image

from jg.hen.core import (
    OutcomeType,
    on_avatar_response,
    on_pinned_repo,
    on_pinned_repos,
    on_profile,
    on_profile_readme,
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
async def has_avatar(avatar_response: httpx.Response) -> tuple[OutcomeType, str]:
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
        return OutcomeType.ERROR, "Nastav si profilový obrázek."
    return OutcomeType.DONE, "Vlastní profilový obrázek máš nastavený."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_name(user: PublicUser) -> tuple[OutcomeType, str]:
    if user.name:
        return OutcomeType.DONE, f"Jméno máš vyplněné: {user.name}"
    return OutcomeType.ERROR, "Doplň si jméno."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(user: PublicUser) -> tuple[OutcomeType, str]:
    if user.bio:
        return OutcomeType.DONE, "Bio máš vyplněné"
    return OutcomeType.INFO, "Doplň si bio."


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(user: PublicUser) -> tuple[OutcomeType, str]:
    if user.location:
        return (OutcomeType.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return OutcomeType.INFO, "Doplň si lokaci."


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(social_accounts: list[SocialAccount]) -> tuple[OutcomeType, str]:
    for account in social_accounts:
        if account.provider == "linkedin":
            return OutcomeType.DONE, f"LinkedIn máš vyplněný: {account.url}"
    return OutcomeType.ERROR, "Doplň si odkaz na svůj LinkedIn profil."


@rule(
    on_profile_readme,
    "https://junior.guru/handbook/github-profile/#profilove-readme",
)
async def has_profile_readme(readme: str | None) -> tuple[OutcomeType, str]:
    if readme:
        return OutcomeType.DONE, "Máš profilové README."
    return OutcomeType.INFO, "Můžeš si vytvořit profilové README."


@rule(
    on_pinned_repos,
    "https://junior.guru/handbook/github-profile/#vypichni-to-cim-se-chlubis",
)
async def has_some_pinned_repos(
    pinned_repos: list[FullRepository],
) -> tuple[OutcomeType, str]:
    pinned_repos_count = len(pinned_repos)
    if pinned_repos_count:
        return (
            OutcomeType.DONE,
            f"Máš nějaké připnuté repozitáře (celkem {pinned_repos_count})",
        )
    return (OutcomeType.ERROR, "Připni si repozitáře, kterými se chceš chlubit.")


@rule(
    on_pinned_repo,
    "https://junior.guru/handbook/github-profile/#popis-repozitare",
)
async def has_pinned_repo_with_description(
    pinned_repo: FullRepository,
) -> tuple[OutcomeType, str]:
    if pinned_repo.description:
        return (
            OutcomeType.DONE,
            f"U připnutého repozitáře {pinned_repo.html_url} máš popisek.",
        )
    return (OutcomeType.ERROR, f"Přidej popisek k repozitáři {pinned_repo.html_url}.")


@rule(
    on_pinned_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_pinned_recent_repo(
    pinned_repo: FullRepository, today: date | None = None
) -> tuple[OutcomeType, str]:
    today = today or date.today()
    pushed_on = pinned_repo.pushed_at.date()
    if pushed_on > today - RECENT_REPO_THRESHOLD:
        return (
            OutcomeType.DONE,
            f"Na připnutém repozitáři {pinned_repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}, což je celkem nedávno.",
        )
    return (
        OutcomeType.WARNING,
        f"Na repozitáři {pinned_repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. Zvaž, zda má být takto starý kód připnutý na tvém profilu.",
    )


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_old_repo_archived(
    repo: FullRepository, today: date | None = None
) -> tuple[OutcomeType, str] | None:
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
            OutcomeType.DONE,
            f"Repozitář {repo.html_url} je celkem starý (poslední změna {pushed_on:%-d.%-m.%Y}). Je dobře, že je archivovaný.",
        )
    else:
        return (
            OutcomeType.WARNING,
            f"Na repozitáři {repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. Možná by šlo repozitář archivovat.",
        )
