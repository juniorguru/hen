import pytest
from githubkit.rest import PublicUser, SocialAccount
from pydantic import TypeAdapter

from jg.hen.models import Status
from jg.hen.rules.has_linkedin import has_linkedin


@pytest.mark.asyncio
async def test_rule_has_linkedin_done(user: PublicUser):
    social_accounts = TypeAdapter(list[SocialAccount]).validate_python(
        [
            {"provider": "linkedin", "url": "https://www.linkedin.com/in/honzajavorek"},
            {"provider": "mastodon", "url": "https://mastodonczech.cz/@honzajavorek"},
        ]
    )
    result = await has_linkedin(None, social_accounts=social_accounts, user=user)

    assert result
    assert result.status == Status.DONE
    assert "https://www.linkedin.com/in/honzajavorek" in result.message


@pytest.mark.asyncio
async def test_rule_has_linkedin_error(user: PublicUser):
    social_accounts = TypeAdapter(list[SocialAccount]).validate_python(
        [
            {"provider": "mastodon", "url": "https://mastodonczech.cz/@honzajavorek"},
        ]
    )
    result = await has_linkedin(None, social_accounts=social_accounts, user=user)

    assert result
    assert result.status == Status.ERROR


@pytest.mark.asyncio
async def test_rule_has_linkedin_warning(user: PublicUser):
    user.blog = "https://www.linkedin.com/in/honzajavorek"
    social_accounts = TypeAdapter(list[SocialAccount]).validate_python([])
    result = await has_linkedin(None, social_accounts=social_accounts, user=user)

    assert result
    assert result.status == Status.WARNING
