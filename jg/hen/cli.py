import asyncio
import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Callable, Coroutine

import click
from slugify import slugify

from jg.hen.core import check_profile_url
from jg.hen.models import Summary


@click.command()
@click.argument("profile_url")
@click.option("-d", "--debug", default=False, is_flag=True, help="Show debug logs.")
@click.option(
    "-r",
    "--record-data",
    default=False,
    is_flag=True,
    help="Record data for testing purposes.",
)
@click.option(
    "--data-dir",
    default=Path(__file__).parent.parent.parent / ".data",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to store recorded data.",
)
@click.option("--github-api-key", envvar="GITHUB_API_KEY", help="GitHub API key.")
def main(
    profile_url: str,
    debug: bool,
    record_data: bool,
    data_dir: Path,
    github_api_key: str | None = None,
):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    if record_data:
        shutil.rmtree(data_dir, ignore_errors=True)
        data_dir.mkdir()
    summary: Summary = asyncio.run(
        check_profile_url(
            profile_url,
            raise_on_error=debug,
            record_data=create_data_recorder(data_dir) if record_data else None,
            github_api_key=github_api_key,
        )
    )
    click.echo(summary.model_dump_json(indent=2))
    if summary.error:
        raise click.Abort()


def create_data_recorder(
    data_dir: Path,
) -> Callable[[str, Any], Coroutine[None, None, None]]:
    async def record_data(key: str, data: Any) -> None:
        hash = hashlib.sha256(key.encode()).hexdigest()[:8]
        slug = slugify(key.removeprefix("https://api.github.com"), max_length=50)
        path = data_dir / f"{hash}-{slug}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    return record_data
