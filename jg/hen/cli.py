import asyncio
import logging

import click

from jg.hen.core import check_profile_url, to_json


@click.command()
@click.argument("profile_url")
@click.option("-d", "--debug", default=False, is_flag=True, help="Show debug logs.")
@click.option("--github-api-key", envvar="GITHUB_API_KEY", help="GitHub API key.")
def main(profile_url: str, debug: bool, github_api_key: str | None = None):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    summary = asyncio.run(
        check_profile_url(
            profile_url,
            raise_on_error=debug,
            github_api_key=github_api_key,
        )
    )
    click.echo(to_json(summary))
    if summary.error:
        raise click.Abort()
