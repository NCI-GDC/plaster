from types import ModuleType

import psqlgraph


def test_get_related_case_edge_cls_name(graph_classes: ModuleType) -> None:
    sample = graph_classes.Sample("sample_1")

    edge_name = graph_classes.utils.get_related_case_edge_cls_name(sample)

    assert edge_name == "SampleRelatesToCase"


def test_get_edge_src_and_get_edge_dst(
    g: psqlgraph.PsqlGraphDriver, graph_classes: ModuleType
) -> None:
    with g.session_scope() as s:
        project = graph_classes.Project("project_1")
        case = graph_classes.Case("case_1")
        case.projects = [project]
        s.merge(case)

        # need to get the node from the database again to reflect the changes.
        # This test needs the graph driver to work
        project = g.nodes().get("project_1")
        assert len(project.edges_in) == 1
        edge = project.edges_in[0]

        src = graph_classes.utils.get_edge_src(edge)
        assert src.node_id == "case_1"

        dst = graph_classes.utils.get_edge_dst(edge)
        assert dst.node_id == "project_1"
