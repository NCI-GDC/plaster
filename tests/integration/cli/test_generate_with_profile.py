from os import PathLike
from pathlib import Path

from click.testing import CliRunner

import plaster
from plaster import cli


def test_version(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"version {plaster.VERSION}" in result.output


def test_echo(cli_runner: CliRunner, app_settings: str) -> None:
    result = cli_runner.invoke(cli.app, ["--config-file", app_settings, "echo"])
    print(result.exception)
    assert result.exit_code == 0


def test_dict_bad_location(
    cli_runner: CliRunner, app_settings: str, tmpdir: PathLike
) -> None:
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "dictionary_bad_location", "-o", tmpdir],
    )
    assert result.exit_code != 0


def test_dict_bad_profile(
    cli_runner: CliRunner, app_settings: str, tmpdir: PathLike
) -> None:
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "dictionary_bad_profile", "-o", tmpdir],
    )
    assert result.exit_code != 0


def test_generation(cli_runner: CliRunner, app_settings: str, tmpdir: PathLike) -> None:
    result = cli_runner.invoke(
        cli.app, ["-c", app_settings, "generate", "-p", "dictionary", "-o", tmpdir]
    )
    assert result.exit_code == 0

    assert Path(f"{tmpdir}/program.py").exists()
    assert Path(f"{tmpdir}/project.py").exists()
    assert Path(f"{tmpdir}/case.py").exists()
    assert Path(f"{tmpdir}/sample.py").exists()
    assert Path(f"{tmpdir}/annotationrelatestocase.py").exists()
