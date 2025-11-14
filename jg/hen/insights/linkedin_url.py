from urllib.parse import quote, urlparse, urlunparse

from githubkit.rest import PublicUser, SocialAccount

from jg.hen.signals import insight, on_social_accounts


@insight(on_social_accounts)
async def linkedin_url(
    social_accounts: list[SocialAccount], user: PublicUser
) -> str | None:
    for account in social_accounts:
        if account.provider == "linkedin":
            parsed_url = urlparse(account.url)
            url_path = quote(parsed_url.path)
            encoded_url = urlunparse(
                (parsed_url.scheme, parsed_url.netloc, url_path, "", "", "")
            )
            return encoded_url
