import logging
import os
import sys
from typing import Optional

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
@click.option(
    "-o", "--output-dir", type=click.Path(), help="Output directory to generate source"
)
@click.option(
    "-s",
    "--schema-dir",
    type=click.Path(),
    default=None,
    help="Output directory for partial schema",
)
@click.pass_obj
def generate(
    cfg: config.PlasterConfig, profile: str, output_dir: str, schema_dir: Optional[str]
) -> None:
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
            is_tag=profile_cfg.get("is_git_tag", True),
        )

    if dictionary is None:
        logger.error(f"Could not load dictionary for {profile_cfg}")
        sys.exit("Dictionary not loaded")

    generator.generate(dictionary, output_dir, namespace=namespace)

    if schema_dir is not None:
        generator.write_partial_schema(dictionary, schema_dir)


@app.command(name="generate-no-profile", help="Generate source code")
@click.option("--dict-name", help="dictionary name, used by psqlgml", default="gdcdictionary")
@click.option("--dict-version", help="dictionary version, used by psqlgml", required=True)
@click.option("-n", "--namespace", help="dictionary namespace, used by plaster", default=None)
@click.option(
    "-i",
    "--input-dir",
    help="dictionary base location, used by psqlgml",
    type=click.Path(),
    default=os.getcwd(),
)
@click.option(
    "-o", "--output-dir", type=click.Path(), help="Output directory to generate source"
)
@click.option(
    "-s",
    "--schema-dir",
    type=click.Path(),
    default=None,
    help="Output directory for partial schema",
)
def generate_without_profile(
    dict_name: str,
    dict_version: str,
    input_dir: Optional[str],
    output_dir: str,
    schema_dir: Optional[str],
    namespace: Optional[str],
) -> None:
    dictionary = psqlgml.load_local(
        name=dict_name,
        version=dict_version,
        dictionary_location=input_dir,
    )

    if dictionary is None:
        logger.error(
            f"Could not load dictionary for name={dict_name}, version={dict_version}, path={input_dir}"
        )
        sys.exit("Dictionary not loaded")

    generator.generate(dictionary, output_dir, namespace=namespace)

    if schema_dir is not None:
        generator.write_partial_schema(dictionary, schema_dir)


if __name__ == "__main__":
    app()
