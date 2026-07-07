import httpx
import pytest
import stamina

from jg.hen.core import fetch_demo


@pytest.fixture(autouse=True)
def no_backoff():
    stamina.set_testing(True, attempts=3)
    yield
    stamina.set_testing(False)


TransportWithRequests = tuple[httpx.MockTransport, list[httpx.Request]]


def responses_transport(*status_codes: int) -> TransportWithRequests:
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
