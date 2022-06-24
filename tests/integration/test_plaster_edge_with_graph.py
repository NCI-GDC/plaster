import warnings
from types import ModuleType

import psqlgraph
import pytest
from sqlalchemy import MetaData
from sqlalchemy import exc as sa_exc


def tear_down_graph(graph):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)

        m = MetaData(graph.engine)
        m.reflect()
        for tbl in reversed(m.sorted_tables):
            graph.engine.execute(tbl.delete())

        # close connection to database
        graph.engine.dispose()


@pytest.fixture
def g(graph_classes) -> psqlgraph.PsqlGraphDriver:
    _g = psqlgraph.PsqlGraphDriver(
        host="localhost", password="test", user="test", database="plaster"
    )
    psqlgraph.create_all(_g.engine)
    yield _g
    tear_down_graph(_g)


def test_pg_links_for_edges_out(graph_classes: ModuleType, g: psqlgraph.PsqlGraphDriver) -> None:
    with g.session_scope() as s:
        project = graph_classes.Project("project_1")
        case = graph_classes.Case("case_1")
        case.projects = [project]
        s.merge(case)

    with g.session_scope():
        project = g.nodes().get("project_1")
        assert len(project.edges_in) == 1
        assert project.edges_in[0].label == "member_of"
        assert project.edges_in[0].src_id == "case_1"

        case = g.nodes().get("case_1")
        assert len(case.edges_out) == 1
        assert case.edges_out[0].label == "member_of"
        assert case.edges_out[0].dst_id == "project_1"


def test_pg_backrefs_for_edges_in(
    graph_classes: ModuleType, g: psqlgraph.PsqlGraphDriver
) -> None:
    with g.session_scope() as s:
        project = graph_classes.Project("project_1")
        case = graph_classes.Case("case_1")
        project.cases = [case]
        s.merge(case)

    with g.session_scope():
        project = g.nodes().get("project_1")
        assert len(project.edges_in) == 1
        assert project.edges_in[0].label == "member_of"
        assert project.edges_in[0].src_id == "case_1"

        case = g.nodes().get("case_1")
        assert len(case.edges_out) == 1
        assert case.edges_out[0].label == "member_of"
        assert case.edges_out[0].dst_id == "project_1"
