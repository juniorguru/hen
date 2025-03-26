import asyncio
import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Callable, Coroutine, TypeVar

from githubkit import Response
from slugify import slugify


ParsedData = TypeVar("ParsedData")

DataRecorder = Callable[[str, Any], Coroutine[None, None, None]]

ResponseProcessor = Callable[[Response[ParsedData]], Coroutine[None, None, ParsedData]]


logger = logging.getLogger("jg.hen.data")


def flush_dir(dir_path: Path) -> None:
    logger.debug(f"Flushing {dir_path}")
    shutil.rmtree(dir_path, ignore_errors=True)
    dir_path.mkdir()


def create_data_recorder(data_dir: Path) -> DataRecorder:
    def _record_data(key: str, data: Any) -> None:
        hash = hashlib.sha256(key.encode()).hexdigest()[:8]
        slug = slugify(key.removeprefix("https://api.github.com"), max_length=50)
        path = data_dir / f"{hash}-{slug}.json"
        logger.info(f"Recording {key!r} to '.data/{path.name}'")
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    async def record_data(key: str, data: Any) -> None:
        await asyncio.to_thread(_record_data, key, data)

    return record_data


def get_response_processor(record_data: DataRecorder | None) -> ResponseProcessor:
    async def process_response(response: Response[ParsedData]) -> ParsedData:
        if record_data:
            await record_data(str(response.url), response.json())
        return response.parsed_data

    return process_response
