import re

from lxml import html

from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo, rule


@rule(on_repo, "https://junior.guru/handbook/github-profile/")  # TODO
async def has_pinned_repo_with_images(context: RepositoryContext) -> RuleResult | None:
    if context.pin_index is None:
        return None
    if not context.readme:
        return None
    html_tree = html.fromstring(context.readme)
    if len(html_tree.cssselect("img")) > 0:
        return (
            Status.DONE,
            f"README připnutého repozitáře {context.repo.html_url} obsahuje obrázky.",
        )
    if re.search(r"!\[[^\]]+\]\([^\)]+\)", context.readme):
        return (
            Status.DONE,
            f"README připnutého repozitáře {context.repo.html_url} obsahuje obrázky.",
        )
    return (
        Status.WARNING,
        f"Připnutý repozitář {context.repo.html_url} má README bez ukázkových obrázků.",
    )
