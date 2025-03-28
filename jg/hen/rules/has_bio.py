from githubkit.rest import PublicUser

from jg.hen.models import Status
from jg.hen.signals import RuleResult, on_profile, rule


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_bio(user: PublicUser) -> RuleResult:
    if user.bio:
        return (Status.DONE, "Bio máš vyplněné")
    return (Status.INFO, "Doplň si bio.")
