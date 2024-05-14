from datetime import date, timedelta
from io import BytesIO

import httpx
from githubkit.rest import PublicUser, SocialAccount
from PIL import Image

from jg.hen.core import (
    RepositoryContext,
    Status,
    on_avatar_response,
    on_profile,
    on_repo,
    on_repos,
    on_social_accounts,
    rule,
)


IDENTICON_GREY = (240, 240, 240)

RECENT_REPO_THRESHOLD = timedelta(days=2 * 365)


@rule(
    on_avatar_response,
    "https://junior.guru/handbook/github-profile/#nastav-si-vlastni-obrazek",
)
async def has_avatar(avatar_response: httpx.Response) -> tuple[Status, str]:
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


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_name(user: PublicUser) -> tuple[Status, str]:
    if user.name:
        return (Status.DONE, f"Jméno máš vyplněné: {user.name}")
    return (Status.ERROR, "Doplň si jméno.")


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(user: PublicUser) -> tuple[Status, str]:
    if user.bio:
        return (Status.DONE, "Bio máš vyplněné")
    return (Status.INFO, "Doplň si bio.")


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(user: PublicUser) -> tuple[Status, str]:
    if user.location:
        return (Status.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return (Status.INFO, "Doplň si lokaci.")


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(social_accounts: list[SocialAccount]) -> tuple[Status, str]:
    for account in social_accounts:
        if account.provider == "linkedin":
            return (Status.DONE, f"LinkedIn máš vyplněný: {account.url}")
    return (Status.ERROR, "Doplň si odkaz na svůj LinkedIn profil.")


@rule(
    on_repos,
    "https://junior.guru/handbook/github-profile/#profilove-readme",
)
async def has_profile_readme(contexts: list[RepositoryContext]) -> tuple[Status, str]:
    for context in contexts:
        if context.is_profile and context.readme:
            return (Status.DONE, "Máš profilové README.")
    return (Status.INFO, "Můžeš si vytvořit profilové README.")


@rule(
    on_repos,
    "https://junior.guru/handbook/github-profile/#vypichni-to-cim-se-chlubis",
)
async def has_some_pinned_repos(
    contexts: list[RepositoryContext],
) -> tuple[Status, str]:
    pinned_repos = [context.repo for context in contexts if context.pin is not None]
    if pinned_repos_count := len(pinned_repos):
        return (
            Status.DONE,
            f"Máš nějaké připnuté repozitáře (celkem {pinned_repos_count})",
        )
    return (Status.ERROR, "Připni si repozitáře, kterými se chceš chlubit.")


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#popis-repozitare",
)
async def has_pinned_repo_with_description(
    context: RepositoryContext,
) -> tuple[Status, str] | None:
    if context.pin is None:
        return None
    if context.repo.description:
        return (
            Status.DONE,
            f"U připnutého repozitáře {context.repo.html_url} máš popisek.",
        )
    return (Status.ERROR, f"Přidej popisek k repozitáři {context.repo.html_url}.")


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_pinned_recent_repo(
    context: RepositoryContext, today: date | None = None
) -> tuple[Status, str] | None:
    if context.pin is None:
        return None
    today = today or date.today()
    pushed_on = context.repo.pushed_at.date()
    if pushed_on > today - RECENT_REPO_THRESHOLD:
        return (
            Status.DONE,
            f"Na připnutém repozitáři {context.repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}, "
            "což je celkem nedávno.",
        )
    return (
        Status.WARNING,
        f"Na repozitáři {context.repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. "
        "Zvaž, zda má být takto starý kód připnutý na tvém profilu.",
    )


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_old_repo_archived(
    context: RepositoryContext, today: date | None = None
) -> tuple[Status, str] | None:
    today = today or date.today()

    if context.repo.fork:
        return None
    if context.repo.pushed_at is None:
        return None

    pushed_on = context.repo.pushed_at.date()
    if pushed_on > today - RECENT_REPO_THRESHOLD:
        return None

    if context.repo.archived:
        return (
            Status.DONE,
            f"Repozitář {context.repo.html_url} je celkem starý (poslední změna {pushed_on:%-d.%-m.%Y}). "
            "Je dobře, že je archivovaný.",
        )
    else:
        return (
            Status.WARNING,
            f"Na repozitáři {context.repo.html_url} se naposledy pracovalo {pushed_on:%-d.%-m.%Y}. "
            "Možná by šlo repozitář archivovat.",
        )
