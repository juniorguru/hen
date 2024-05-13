from typing import Any, AsyncGenerator

import httpx

from jg.hen.core import insight, on_avatar_response


@insight(on_avatar_response)
async def avatar_url(
    avatar_response: httpx.Response,
) -> AsyncGenerator[tuple[str, Any], None]:
    yield "avatar_url", str(avatar_response.url)
