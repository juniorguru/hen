import httpx
import stamina


def is_demo_server_error(exc: BaseException) -> bool:
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500


@stamina.retry(on=is_demo_server_error, attempts=3)
async def _fetch_demo(http: httpx.AsyncClient, homepage_url: str) -> httpx.Response:
    response = await http.get(homepage_url, follow_redirects=True, timeout=10.0)
    response.raise_for_status()  # this must happen to trigger stamina retries
    return response


async def fetch_demo(
    http: httpx.AsyncClient, homepage_url: str
) -> httpx.Response | Exception:
    try:
        return await _fetch_demo(http, homepage_url)
    except httpx.HTTPStatusError as e:
        return e.response
    except Exception as e:
        return e


def get_demo_url(result: httpx.Response | Exception | None) -> str | None:
    if not result:
        return None
    if isinstance(result, Exception):
        return None
    try:
        result.raise_for_status()
    except httpx.HTTPStatusError:
        return None
    return str(result.url)
