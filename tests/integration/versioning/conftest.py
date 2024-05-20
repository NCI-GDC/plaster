import sys

import psqlgml
import pytest
from click.testing import CliRunner

from plaster import cli, config


@pytest.fixture(scope="session")
def test_dictionary_versioning(
    plaster_config: config.PlasterConfig, test_data_location: str
) -> psqlgml.Dictionary:
    return psqlgml.load_local(
        version="0.1.0", name="version_dict", dictionary_location=test_data_location
    )


@pytest.fixture(scope="session")
def graph_classes_versioning(cli_runner: CliRunner, app_settings: str, tmpdir_factory) -> None:
    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "version_dict", "-o", tmpdir / "version_module"],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import version_module

    return version_module
