from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo, rule


@rule(on_repo, "https://junior.guru/handbook/github-profile/")
async def has_pinned_repo_with_readme(context: RepositoryContext) -> RuleResult | None:
    if context.pin_index is None:
        return None
    if context.readme and context.readme.strip():
        return (
            Status.DONE,
            f"U připnutého repozitáře {context.repo.html_url} máš README.",
        )
    return (Status.ERROR, f"Přidej README k repozitáři {context.repo.html_url}.")
