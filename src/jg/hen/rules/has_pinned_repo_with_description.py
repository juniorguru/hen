from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import on_repo, rule


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
