import httpx

from jg.hen.models import RepositoryContext, Status
from jg.hen.signals import RuleResult, on_repo_demo, rule


@rule(
    on_repo_demo,
    "https://junior.guru/handbook/github-profile/",  # TODO
)
async def has_pinned_repo_with_working_demo(
    demo_response: httpx.Response | None, context: RepositoryContext
) -> RuleResult | None:
    if demo_response is None:
        return None
    try:
        demo_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return (
            Status.ERROR,
            f"Repozitář {context.repo.html_url} má ukázku na adrese {demo_response.url}, ale ta vrací chybu {e.response.status_code}.",
        )
    else:
        return (
            Status.DONE,
            f"Repozitář {context.repo.html_url} má ukázku na adrese {demo_response.url} a ta je funkční.",
        )
