from githubkit.rest import PublicUser

from jg.hen.models import Status
from jg.hen.signals import RuleResult, on_profile, rule


@rule(
    on_profile,
    "https://junior.guru/handbook/github-profile/#vypln-si-zakladni-udaje",
)
async def has_email(user: PublicUser) -> RuleResult:
    if user.email:
        return (Status.DONE, f"E-mail máš vyplněný: {user.email}")
    return (
        Status.WARNING,
        "Doplň si veřejný e-mail, ať tě zaměstnavatelé mohou spolehlivěji kontaktovat.",
    )
