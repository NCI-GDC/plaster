import logging

import click

from plaster import VERSION, config

logger: logging.Logger


@click.group()
@click.version_option(VERSION)
@click.option("-c", "--config-file", type=click.Path(exists=True), help="Path to config file")
def app(config_file: str) -> None:
    """Entry script"""
    global logger

    config.load_config(config_file)
    logger = logging.getLogger(__name__)


@app.command(name="echo", help="Simple ping functionality")
def echo() -> None:
    logger.info("Echo requested")
