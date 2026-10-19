import httpx2
import pytest

from jg.hen.models import RepositoryContext, Status
from jg.hen.rules.has_pinned_repo_with_working_demo import (
    has_pinned_repo_with_working_demo,
)


def response(
    status_code: int, headers: dict[str, str] | None = None
) -> httpx2.Response:
    request = httpx2.Request("GET", "https://demo.example.com")
    return httpx2.Response(status_code, headers=headers, request=request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "demo_result, expected",
    [
        pytest.param(response(200), Status.DONE, id="ok"),
        pytest.param(response(404), Status.ERROR, id="not-found"),
        pytest.param(response(403), Status.ERROR, id="forbidden"),
        pytest.param(
            response(403, {"Server": "cloudflare"}), Status.WARNING, id="cloudflare"
        ),
        pytest.param(response(429), Status.WARNING, id="rate-limited"),
        pytest.param(httpx2.ConnectError("nope"), Status.WARNING, id="exception"),
    ],
)
async def test_rule_has_pinned_repo_with_working_demo(
    context: RepositoryContext,
    demo_result: httpx2.Response | Exception,
    expected: Status,
):
    result = await has_pinned_repo_with_working_demo(
        None, demo_result=demo_result, context=context
    )

    assert result
    assert result.status == expected
