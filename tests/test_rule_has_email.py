import pytest
from githubkit.rest import PublicUser

from jg.hen.models import Status
from jg.hen.rules.has_email import has_email


@pytest.mark.asyncio
async def test_rule_has_email_done(user: PublicUser):
    user.email = "mail@honzajavorek.cz"

    result = await has_email(None, user=user)

    assert result
    assert result.status == Status.DONE
    assert "mail@honzajavorek.cz" in result.message


@pytest.mark.asyncio
async def test_rule_has_email_warning(user: PublicUser):
    user.email = None

    result = await has_email(None, user=user)

    assert result
    assert result.status == Status.WARNING
