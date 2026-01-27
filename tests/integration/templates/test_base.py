import sys
from types import ModuleType

import pytest
from click.testing import CliRunner

from plaster import cli


@pytest.fixture(scope="session")
def graph_classes_versioning(cli_runner: CliRunner, app_settings: str, tmpdir_factory) -> None:
    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        [
            "-c",
            app_settings,
            "generate",
            "-p",
            "version_dict",
            "-o",
            tmpdir / "version_module",
        ],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import version_module

    return version_module


def test_default_namespace_is_none(graph_classes: ModuleType) -> None:
    """Test default namespace is None.

        Given generated datamodels
        When no namespace is provided in toml file
        And no environment variable is set
        Then the dictionary should have namespace None

    Args:
        graph_classes: all node and edge classes
    """
    assert graph_classes.namespace is None


def test_get_namespace_from_toml(graph_classes_versioning: ModuleType) -> None:
    """Test get namespace from toml.

        Given generated datamodels
        When a namespace is provided in the toml file
        And no environment variable is set
        Then the dictionary should have the namespace from the toml

    Args:
        graph_classes_versioning: all node and edge classes
    """
    assert graph_classes_versioning.namespace == "version_dict"


def test_env_namespace_overwrite_default(
    cli_runner: CliRunner,
    app_settings: str,
    tmpdir_factory,
    monkeypatch,
) -> None:
    """Test get namespace from env overwrite default.

        Given the right environment variable and generated datamodels
        When no namespace is provided in the toml file
        And correct environment variable is set
        Then the dictionary should have the namespace from the env var

    Args:
        cli_runner: Cli Runner
        app_settings: string for the location of the config toml
        tmpdir_factory: temporary location to generate models
        monkeypatch: monkeypatch to set the env
    """
    monkeypatch.setenv("DICTIONARY_NAMESPACE", "yiersansiwu")

    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        [
            "-c",
            app_settings,
            "generate",
            "-p",
            "dictionary",
            "-o",
            tmpdir / "shangshandalaohu",
        ],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import shangshandalaohu

    assert shangshandalaohu.namespace == "yiersansiwu"


def test_env_namespace_overwrite_toml(
    cli_runner: CliRunner,
    app_settings: str,
    tmpdir_factory,
    monkeypatch,
) -> None:
    """Test get namespace from env overwrite toml.

        Given the right environment variable and generated datamodels
        When a namespace is provided in the toml file
        And correct environment variable is set
        Then the dictionary should have the namespace from the env var

    Args:
        cli_runner: Cli Runner
        app_settings: string for the location of the config toml
        tmpdir_factory: temporary location to generate models
        monkeypatch: monkeypatch to set the env
    """
    monkeypatch.setenv("VERSION_DICT_NAMESPACE", "laohumeidazhao")

    tmpdir = tmpdir_factory.mktemp("tmp")
    result = cli_runner.invoke(
        cli.app,
        [
            "-c",
            app_settings,
            "generate",
            "-p",
            "version_dict",
            "-o",
            tmpdir / "pengdaoxiaosongshu",
        ],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import pengdaoxiaosongshu

    assert pengdaoxiaosongshu.namespace == "laohumeidazhao"
