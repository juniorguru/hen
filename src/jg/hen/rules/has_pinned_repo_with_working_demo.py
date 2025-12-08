import httpx

from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo_demo, rule


@rule(
    on_repo_demo,
    "https://junior.guru/handbook/github-profile/",  # TODO
)
async def has_pinned_repo_with_working_demo(
    demo_result: httpx.Response | Exception, context: RepositoryContext
) -> RuleResult | None:
    if isinstance(demo_result, Exception):
        return (
            Status.WARNING,
            f"Repozitář {context.repo.html_url} má ukázku na adrese {context.repo.homepage}, ale nedaří se ji načíst: {demo_result}",
        )
    try:
        demo_result.raise_for_status()
    except httpx.HTTPStatusError as e:
        return (
            Status.ERROR,
            f"Repozitář {context.repo.html_url} má ukázku na adrese {demo_result.url}, ale ta vrací chybu {e.response.status_code}.",
        )
    return (
        Status.DONE,
        f"Repozitář {context.repo.html_url} má ukázku na adrese {demo_result.url} a ta je funkční.",
    )
