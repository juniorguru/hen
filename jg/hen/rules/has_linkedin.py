from githubkit.rest import SocialAccount

from jg.hen.models import Status
from jg.hen.signals import on_social_accounts, rule


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(social_accounts: list[SocialAccount]) -> tuple[Status, str]:
    for account in social_accounts:
        if account.provider == "linkedin":
            return (Status.DONE, f"LinkedIn máš vyplněný: {account.url}")
    return (Status.ERROR, "Doplň si odkaz na svůj LinkedIn profil.")
