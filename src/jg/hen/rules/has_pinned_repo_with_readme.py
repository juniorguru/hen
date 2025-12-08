from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo, rule


MIN_README_LENGTH = 500


@rule(on_repo, "https://junior.guru/handbook/github-profile/")  # TODO
async def has_pinned_repo_with_readme(context: RepositoryContext) -> RuleResult | None:
    if context.pin_index is None:
        return None
    if not context.readme:
        return (Status.ERROR, f"Přidej README k repozitáři {context.repo.html_url}.")
    if len(context.readme.strip()) < MIN_README_LENGTH:
        return (
            Status.ERROR,
            f"README u připnutého repozitáře {context.repo.html_url} je příliš krátké.",
        )
    return (
        Status.DONE,
        f"U připnutého repozitáře {context.repo.html_url} máš README.",
    )
