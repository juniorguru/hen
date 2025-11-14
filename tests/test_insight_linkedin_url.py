import pytest
from githubkit.rest import PublicUser, SocialAccount
from pydantic import TypeAdapter

from jg.hen.insights.linkedin_url import linkedin_url
from jg.hen.models import Insight


@pytest.mark.asyncio
async def test_insight_linkedin_url(user: PublicUser):
    social_accounts = TypeAdapter(list[SocialAccount]).validate_python(
        [
            {"provider": "linkedin", "url": "https://www.linkedin.com/in/honzajavorek"},
            {"provider": "mastodon", "url": "https://mastodonczech.cz/@honzajavorek"},
        ]
    )
    insight = await linkedin_url(None, social_accounts=social_accounts, user=user)

    assert insight == Insight(
        name="linkedin_url",
        value="https://www.linkedin.com/in/honzajavorek",
        collect=False,
    )


@pytest.mark.asyncio
async def test_insight_linkedin_url_encoding(user: PublicUser):
    social_accounts = TypeAdapter(list[SocialAccount]).validate_python(
        [
            {
                "provider": "linkedin",
                "url": "https://www.linkedin.com/in/veronika-obrtelová/",
            },
        ]
    )
    insight = await linkedin_url(None, social_accounts=social_accounts, user=user)

    assert insight == Insight(
        name="linkedin_url",
        value="https://www.linkedin.com/in/veronika-obrtelov%C3%A1/",
        collect=False,
    )
