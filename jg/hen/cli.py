import asyncio
import logging
from dataclasses import asdict
from pprint import pprint

import click

from jg.hen.core import check_profile_url


logger = logging.getLogger("jg.hen.cli")


@click.command()
@click.argument("profile_url")
@click.option("-d", "--debug", default=False, is_flag=True, help="Show debug logs")
def main(profile_url: str, debug: bool):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    logger.info(f"URL: {profile_url}")
    result = asyncio.run(check_profile_url(profile_url, raise_on_error=debug))
    pprint(asdict(result))
