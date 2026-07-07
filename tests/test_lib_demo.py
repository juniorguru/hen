import httpx
import pytest
import stamina

from jg.hen.lib.demo import fetch_demo, get_demo_url, is_demo_server_error


def status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError("boom", request=request, response=response)


def response(status_code: int, url: str = "https://demo.example.com") -> httpx.Response:
    return httpx.Response(status_code, request=httpx.Request("GET", url))


@pytest.fixture(autouse=True)
def no_backoff():
    stamina.set_testing(True, attempts=3)
    yield
    stamina.set_testing(False)


def responses_transport(
    *status_codes: int,
) -> tuple[httpx.MockTransport, list[httpx.Request]]:
    codes = iter(status_codes)
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(next(codes), request=request)

    return httpx.MockTransport(handler), requests


@pytest.mark.asyncio
async def test_fetch_demo_succeeds_on_first_try():
    transport, requests = responses_transport(200)
    async with httpx.AsyncClient(transport=transport) as http:
        result = await fetch_demo(http, "https://example.com")

    assert isinstance(result, httpx.Response)
    assert result.status_code == 200
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_fetch_demo_retries_on_server_error_then_succeeds():
    transport, requests = responses_transport(503, 502, 200)
    async with httpx.AsyncClient(transport=transport) as http:
        result = await fetch_demo(http, "https://example.com")

    assert isinstance(result, httpx.Response)
    assert result.status_code == 200
    assert len(requests) == 3


@pytest.mark.asyncio
async def test_fetch_demo_gives_up_after_repeated_server_errors():
    transport, requests = responses_transport(503, 503, 503)
    async with httpx.AsyncClient(transport=transport) as http:
        result = await fetch_demo(http, "https://example.com")

    assert isinstance(result, httpx.Response)
    assert result.status_code == 503
    assert len(requests) == 3


@pytest.mark.asyncio
async def test_fetch_demo_does_not_retry_on_client_error():
    transport, requests = responses_transport(404)
    async with httpx.AsyncClient(transport=transport) as http:
        result = await fetch_demo(http, "https://example.com")

    assert isinstance(result, httpx.Response)
    assert result.status_code == 404
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_fetch_demo_does_not_retry_on_connection_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        result = await fetch_demo(http, "https://example.com")

    assert isinstance(result, httpx.ConnectError)


@pytest.mark.parametrize(
    "exc, expected",
    [
        pytest.param(status_error(500), True, id="500-internal-error"),
        pytest.param(status_error(502), True, id="502-bad-gateway"),
        pytest.param(status_error(503), True, id="503-unavailable"),
        pytest.param(status_error(599), True, id="599-upper-bound"),
        pytest.param(status_error(400), False, id="400-bad-request"),
        pytest.param(status_error(404), False, id="404-not-found"),
        pytest.param(status_error(499), False, id="499-just-below-5xx"),
        pytest.param(httpx.ConnectError("nope"), False, id="connect-error"),
        pytest.param(ValueError("nope"), False, id="non-httpx-error"),
    ],
)
def test_is_demo_server_error(exc: BaseException, expected: bool):
    assert is_demo_server_error(exc) is expected


@pytest.mark.parametrize(
    "result",
    [
        pytest.param(None, id="none"),
        pytest.param(httpx.ConnectError("nope"), id="exception"),
        pytest.param(response(404), id="client-error"),
        pytest.param(response(500), id="server-error"),
    ],
)
def test_get_demo_url_returns_none(result: httpx.Response | Exception | None):
    assert get_demo_url(result) is None


@pytest.mark.parametrize(
    "status_code",
    [
        pytest.param(200, id="200-ok"),
        pytest.param(204, id="204-no-content"),
    ],
)
def test_get_demo_url_returns_url_for_success(status_code: int):
    result = response(status_code, "https://demo.example.com")
    assert get_demo_url(result) == "https://demo.example.com"
