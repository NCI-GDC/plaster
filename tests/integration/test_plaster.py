from os import PathLike
from pathlib import Path
from types import ModuleType

from click.testing import CliRunner
from deepdiff import DeepDiff

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


def test_id(graph_classes: ModuleType) -> None:
    case = graph_classes.Case(node_id="case_id")
    assert case.id == "case_id"
    case.id = "new_case_id"
    assert case.node_id == "new_case_id"


def test_relates_to_case_edges(graph_classes: ModuleType) -> None:
    edge = graph_classes.SampleRelatesToCase
    assert edge.__tablename__ == "edge_samplerelatestocase"
    assert edge.__label__ == "relates_to"
    assert edge.__dst_class__ == "Case"
    assert edge.__dst_table__ == "node_case"
    assert edge.__src_class__ == "Sample"
    assert edge.__src_table__ == "node_sample"

    assert edge.__dst_src_assoc__ == "_related_sample"
    assert edge.__src_dst_assoc__ == "_related_cases"


def test_pg_secondary_keys(graph_classes: ModuleType) -> None:
    Case = graph_classes.Case
    assert DeepDiff(Case._Case__pg_secondary_keys, [["project_id", "submitter_id"]]) == {}


def test_secondary_keys_dict(graph_classes: ModuleType) -> None:
    case = graph_classes.Case("case_1")
    case.project_id = "project_1"
    case.submitter_id = "submitter_1"
    expected = [{"project_id": "project_1", "submitter_id": "submitter_1"}]
    assert DeepDiff(case._secondary_keys_dicts, expected) == {}


def test_secondary_keys(graph_classes: ModuleType) -> None:
    case = graph_classes.Case("case_1")
    case.project_id = "project_1"
    case.submitter_id = "submitter_1"
    expected = (("project_1", "submitter_1"),)
    assert DeepDiff(case._secondary_keys, expected) == {}


def test_secondary_keys_not_pg_property(graph_classes: ModuleType) -> None:
    assert graph_classes.Case._secondary_keys._is_pg_property is False
