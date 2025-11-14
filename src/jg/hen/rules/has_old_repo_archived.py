from datetime import date, timedelta

from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo, rule


OLD_REPO_THRESHOLD = timedelta(days=2 * 365)


@rule(
    on_repo,
    "https://junior.guru/handbook/github-profile/#upozad-stare-veci-a-nedodelky",
)
async def has_old_repo_archived(
    context: RepositoryContext, today: date | None = None
) -> RuleResult | None:
    today = today or date.today()

    if context.repo.fork:
        return None
    if context.repo.pushed_at is None:
        return None

    pushed_on = context.repo.pushed_at.date()
    if pushed_on > today - OLD_REPO_THRESHOLD:
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
