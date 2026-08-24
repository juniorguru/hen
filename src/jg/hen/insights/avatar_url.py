import httpx2

from jg.hen.signals import insight, on_avatar_response


@insight(on_avatar_response)
async def avatar_url(avatar_response: httpx2.Response) -> str:
    return str(avatar_response.url)
