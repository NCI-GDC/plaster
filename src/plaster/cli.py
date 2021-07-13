import logging

import click

import plaster

logger: logging.Logger


@click.group()
@click.version_option(plaster.VERSION)
@click.option("-c", "--config", type=click.Path(exists=True), help="Path to config file")
def app(config: str) -> None:
    """Entry script"""
    global logger

    cfg = plaster.load_config(config)
    cfg.configure_logger()

    logger = logging.getLogger(__name__)


@app.command(name="echo", help="Simple ping functionality")
def echo() -> None:
    logger.info("Echo requested")
