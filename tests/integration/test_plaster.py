import sys
from os import PathLike
from pathlib import Path
from types import ModuleType

import pytest
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


def test_dict_bad_location(cli_runner: CliRunner, app_settings: str, tmpdir: PathLike) -> None:
    result = cli_runner.invoke(
        cli.app, ["-c", app_settings, "generate", "-p", "dictionary_bad_location", "-o", tmpdir]
    )
    assert result.exit_code != 0


def test_dict_bad_profile(cli_runner: CliRunner, app_settings: str, tmpdir: PathLike) -> None:
    result = cli_runner.invoke(
        cli.app, ["-c", app_settings, "generate", "-p", "dictionary_bad_profile", "-o", tmpdir]
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


@pytest.fixture
def graph_classes(cli_runner: CliRunner, app_settings: str, tmpdir: Path) -> None:
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "dictionary", "-o", tmpdir / "test_module"],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import test_module

    return test_module


def test_back_refs(graph_classes: ModuleType) -> None:
    Project = graph_classes.Project
    assert Project._pg_backrefs["cases"]["src_type"] == graph_classes.Case
    assert Project._pg_backrefs["cases"]["name"] == "projects"


def test_pg_links(graph_classes: ModuleType) -> None:
    pg_links = graph_classes.Case._pg_links
    assert pg_links["projects"]["dst_type"] == graph_classes.Project
    assert pg_links["projects"]["edge_out"] == "_CaseMemberOfProject_out"


def test_pg_edges(graph_classes: ModuleType) -> None:
    pg_edges = graph_classes.Project._pg_edges
    assert pg_edges["programs"]["backref"] == "projects"
    assert pg_edges["programs"]["type"] == graph_classes.Program
    assert pg_edges["cases"]["backref"] == "projects"
    assert pg_edges["cases"]["type"] == graph_classes.Case
