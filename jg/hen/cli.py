import logging

import click


logger = logging.getLogger("jg.hen")


@click.command()
@click.argument("profile_url")
@click.option("-d", "--debug", default=False, is_flag=True, help="Show debug logs")
def main(profile_url: str, debug: bool):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    logger.info(f"URL: {profile_url}")
