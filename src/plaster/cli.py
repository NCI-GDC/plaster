import logging
import sys

import click
import psqlgml

from plaster import VERSION, config, generator

logger: logging.Logger


@click.group()
@click.pass_context
@click.version_option(VERSION)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    default="plaster.toml",
    help="Path to config file",
)
def app(ctx: click.Context, config_file: str) -> None:
    """Entry script."""
    global logger

    # pass context
    ctx.obj = config.load_config(config_file)
    logger = logging.getLogger(__name__)


@app.command(name="echo", help="Simple ping functionality")
def echo() -> None:
    logger.info("Echo requested")


@app.command(name="generate", help="Generate source code")
@click.option("-p", "--profile", type=str, help="Name of the profile to generate")
@click.option("-o", "--output-dir", type=click.Path(), help="Output directory to generate source")
@click.pass_obj
def generate(cfg: config.PlasterConfig, profile: str, output_dir: str) -> None:
    profile_cfg = cfg.get_profile(profile)
    if not profile_cfg:
        raise ValueError(f"Unrecognized profile {profile} entered")
    namespace = profile_cfg.get("namespace")

    if profile_cfg.get("type", "local") == "local":
        dictionary = psqlgml.load_local(
            name=profile,
            version=profile_cfg.get("version", "master"),
            dictionary_location=profile_cfg["local_directory"],
        )
    else:
        dictionary = psqlgml.load(
            name=profile,
            git_url=profile_cfg.get("url"),  # type: ignore
            overwrite=profile_cfg.get("overwrite", False),
            schema_path=profile_cfg.get("path", f"{profile}/schemas"),
            version=profile_cfg.get("version", "master"),
            is_tag=profile_cfg.get("is_tag", True),
        )

    if dictionary is None:
        logger.error(f"Could not load dictionary for {profile_cfg}")
        sys.exit("Dictionary not loaded")

    generator.generate(dictionary, output_dir, namespace=namespace)


if __name__ == "__main__":
    app()
