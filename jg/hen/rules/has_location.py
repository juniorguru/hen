from githubkit.rest import PublicUser

from jg.hen.models import Status
from jg.hen.signals import RuleResult, on_profile, rule


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_location(user: PublicUser) -> RuleResult:
    if user.location:
        return (Status.DONE, f"Lokaci máš vyplněnou: {user.location}")
    return (Status.INFO, "Doplň si lokaci.")
