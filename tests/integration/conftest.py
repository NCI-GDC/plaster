import sys
from types import ModuleType

import psqlgml
import psqlgraph
import pytest
from click.testing import CliRunner
from psqlgraph import ext

from plaster import cli
from tests.integration import (
    create_versioned_nodes_tables,
    tear_down_graph,
    truncate_versioned_nodes_tables,
    utils,
)


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_dict() -> psqlgml.Dictionary:
    return psqlgml.load(version="2.4.0")


@pytest.fixture(scope="session")
def graph_classes(cli_runner: CliRunner, app_settings: str, tmpdir_factory) -> None:
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
            tmpdir / "test_module",
        ],
    )
    assert result.exit_code == 0, {"stderr": result.stderr, "stdout": result.stdout}

    sys.path.insert(0, str(tmpdir))
    import test_module

    return test_module


@pytest.fixture
def graph_driver(graph_classes: ModuleType) -> psqlgraph.PsqlGraphDriver:
    g = utils.get_graph_driver(graph_classes.namespace)
    base = psqlgraph.base.ORMBase
    if graph_classes.namespace is not None:
        base = ext.get_orm_base(graph_classes.namespace)
    psqlgraph.create_all(g.engine, base=base)

    create_versioned_nodes_tables(g.engine)

    yield g

    truncate_versioned_nodes_tables(g.engine)

    tear_down_graph(g)
