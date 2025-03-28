from datetime import date, timedelta

from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo, rule


RECENT_REPO_THRESHOLD = timedelta(days=2 * 365)


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_pinned_recent_repo(
    context: RepositoryContext, today: date | None = None
) -> RuleResult | None:
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
