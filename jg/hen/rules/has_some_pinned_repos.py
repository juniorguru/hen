from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repos, rule


@rule(
    on_repos,
    "https://junior.guru/handbook/github-profile/#vypichni-to-cim-se-chlubis",
)
async def has_some_pinned_repos(
    contexts: list[RepositoryContext],
) -> RuleResult:
    pinned_repos = [
        context.repo for context in contexts if context.pin_index is not None
    ]
    if pinned_repos_count := len(pinned_repos):
        return (
            Status.DONE,
            f"Máš nějaké připnuté repozitáře (celkem {pinned_repos_count})",
        )
    return (Status.ERROR, "Připni si repozitáře, kterými se chceš chlubit.")
