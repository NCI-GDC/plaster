import sys

import pytest
from _pytest import tmpdir
from click.testing import CliRunner

from plaster import cli


@pytest.fixture(scope="session")
def graph_classes_versioning(
    cli_runner: CliRunner, app_settings: str, tmpdir_factory: tmpdir.TempdirFactory
) -> None:
    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "version_dict", "-o", tmpdir / "version_module"],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import version_module

    return version_module
