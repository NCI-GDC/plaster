import sys
from pathlib import Path

import psqlgml
import pytest
from _pytest import tmpdir
from click.testing import CliRunner

from plaster import cli


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_dict() -> psqlgml.Dictionary:
    return psqlgml.load(version="2.4.0")


@pytest.fixture(scope="session")
def graph_classes(
    cli_runner: CliRunner, app_settings: str, tmpdir_factory: tmpdir.TempdirFactory
) -> None:
    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "dictionary", "-o", tmpdir / "test_module"],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import test_module

    return test_module
