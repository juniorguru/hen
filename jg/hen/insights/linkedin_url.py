from githubkit.rest import PublicUser, SocialAccount

from jg.hen.signals import insight, on_social_accounts


@insight(on_social_accounts)
async def linkedin_url(
    social_accounts: list[SocialAccount], user: PublicUser
) -> str | None:
    for account in social_accounts:
        if account.provider == "linkedin":
            return account.url
