import sys
import warnings
from pathlib import Path
from types import ModuleType

import psqlgml
import psqlgraph
import pytest
from click.testing import CliRunner
from sqlalchemy import MetaData
from sqlalchemy import exc as sa_exc

from plaster import cli


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_dict() -> psqlgml.Dictionary:
    return psqlgml.load(version="2.4.0")


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


def tear_down_graph(graph: psqlgraph.PsqlGraphDriver) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)

        m = MetaData(graph.engine)
        m.reflect()
        for tbl in reversed(m.sorted_tables):
            graph.engine.execute(tbl.delete())

        # close connection to database
        graph.engine.dispose()


@pytest.fixture
def g(graph_classes: ModuleType) -> psqlgraph.PsqlGraphDriver:
    _g = psqlgraph.PsqlGraphDriver(
        host="localhost", password="test", user="test", database="plaster"
    )
    psqlgraph.create_all(_g.engine)
    yield _g
    tear_down_graph(_g)
