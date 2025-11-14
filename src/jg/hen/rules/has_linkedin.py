from githubkit.rest import PublicUser, SocialAccount

from jg.hen.models import Status
from jg.hen.signals import RuleResult, on_social_accounts, rule


@rule(
    on_social_accounts,
    "https://junior.guru/handbook/github-profile/#zviditelni-sve-dalsi-profily",
)
async def has_linkedin(
    social_accounts: list[SocialAccount], user: PublicUser
) -> RuleResult:
    for account in social_accounts:
        if account.provider == "linkedin":
            return (Status.DONE, f"LinkedIn máš vyplněný: {account.url}")
    if website_url := user.blog:
        if "linkedin.com" in website_url:
            return (
                Status.WARNING,
                f"LinkedIn máš vyplněný: {website_url}, ale je uložený v políčku pro osobní webovku, ne v políčku přímo pro sociální sítě.",
            )
    return (Status.ERROR, "Doplň si odkaz na svůj LinkedIn profil.")
