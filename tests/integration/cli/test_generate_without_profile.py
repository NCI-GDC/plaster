from os import PathLike
from pathlib import Path

from click.testing import CliRunner

import plaster
from plaster import cli


def test_dict_bad_location(cli_runner: CliRunner, tmpdir: PathLike) -> None:
    result = cli_runner.invoke(
        cli.app,
        [
            "generate-no-profile",
            "-i",
            "tests/bad_location",
            "--dict-name",
            "dictionary",
            "--dict-version",
            "0.1.0",
            "-o",
            tmpdir,
        ],
    )
    assert result.exit_code != 0


def test_dict_bad_dictionary(
    cli_runner: CliRunner, test_data_location: PathLike, tmpdir: PathLike
) -> None:
    result = cli_runner.invoke(
        cli.app,
        [
            "generate-no-profile",
            "-i",
            test_data_location,
            "--dict-name",
            "bad_dictionary",
            "--dict-version",
            "0.1.0",
            "-o",
            tmpdir,
        ],
    )
    assert result.exit_code != 0


def test_dict_bad_version(
    cli_runner: CliRunner, test_data_location: PathLike, tmpdir: PathLike
) -> None:
    result = cli_runner.invoke(
        cli.app,
        [
            "generate-no-profile",
            "-i",
            test_data_location,
            "--dict-name",
            "dictionary",
            "--dict-version",
            "0.0.0",
            "-o",
            tmpdir,
        ],
    )
    assert result.exit_code != 0


def test_generation(
    cli_runner: CliRunner, test_data_location: PathLike, tmpdir: PathLike
) -> None:
    result = cli_runner.invoke(
        cli.app,
        [
            "generate-no-profile",
            "-i",
            test_data_location,
            "--dict-name",
            "dictionary",
            "--dict-version",
            "0.1.0",
            "-o",
            tmpdir,
        ],
    )
    assert result.exit_code == 0

    assert Path(f"{tmpdir}/program.py").exists()
    assert Path(f"{tmpdir}/project.py").exists()
    assert Path(f"{tmpdir}/case.py").exists()
    assert Path(f"{tmpdir}/sample.py").exists()
    assert Path(f"{tmpdir}/annotationrelatestocase.py").exists()
