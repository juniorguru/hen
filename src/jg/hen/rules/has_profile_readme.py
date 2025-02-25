from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import on_repos, rule


@rule(
    on_repos,
    "https://junior.guru/handbook/github-profile/#profilove-readme",
)
async def has_profile_readme(contexts: list[RepositoryContext]) -> tuple[Status, str]:
    for context in contexts:
        if context.is_profile and context.readme:
            return (Status.DONE, "Máš profilové README.")
    return (Status.INFO, "Můžeš si vytvořit profilové README.")
