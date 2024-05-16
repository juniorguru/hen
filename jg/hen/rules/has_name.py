from githubkit.rest import PublicUser

from jg.hen.models import Status
from jg.hen.signals import on_profile, rule


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_name(user: PublicUser) -> tuple[Status, str]:
    if user.name:
        return (Status.DONE, f"Jméno máš vyplněné: {user.name}")
    return (Status.ERROR, "Doplň si jméno.")
