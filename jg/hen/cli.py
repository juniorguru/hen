import logging

import click


logger = logging.getLogger("jg.hen")


@click.group()
@click.option("-d", "--debug", default=False, is_flag=True)
def main(debug: bool = False):
    logger.basicConfig(level=logging.DEBUG if debug else logging.INFO)
