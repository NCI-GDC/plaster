from click.testing import CliRunner

import plaster
from plaster import cli


def test_version(cli_runner: CliRunner):
    result = cli_runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"version {plaster.VERSION}" in result.output


def test_echo(cli_runner: CliRunner, app_settings: str):
    result = cli_runner.invoke(cli.app, ["--config", app_settings, "echo"])
    print(result.exception)
    assert result.exit_code == 0
