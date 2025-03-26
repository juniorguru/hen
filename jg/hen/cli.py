import asyncio
import logging
from pathlib import Path

import click

from jg.hen.core import check_profile_url
from jg.hen.data import create_data_recorder, flush_dir
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
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    if record_data:
        flush_dir(data_dir)

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
