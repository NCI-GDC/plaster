from types import ModuleType

import psqlgraph


def test_get_related_case_edge_cls_name(graph_classes: ModuleType) -> None:
    """Test get_related_case_edge_cls_name

        Given a node class
        When get_related_case_edge_cls_name is called
        Then the edge name of the related case edge should be returned

    Args:
        graph_classes: all node and edge classes

    Returns:
        None
    """

    sample = graph_classes.Sample("sample_1")

    edge_name = graph_classes.utils.get_related_case_edge_cls_name(sample)

    assert edge_name == "SampleRelatesToCase"


def test_get_edge_src_and_get_edge_dst(
    graph_driver: psqlgraph.PsqlGraphDriver, graph_classes: ModuleType
) -> None:
    """test get edge src and get edge dst.

        Given an edge between 2 nodes
        When get_edge_src is called
        Then the source node should be returned

        Given an edge between 2 nodes
        When get_edge_dst is called
        Then the destination node should be returned

    Args:
        g: psqlgraph driver
        graph_classes: all node and edge classes

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        project = graph_classes.Project("project_1")
        case = graph_classes.Case("case_1")
        case.projects = [project]
        s.merge(case)

        # need to get the node from the database again to reflect the changes.
        # This test needs the graph driver to work
        project = graph_driver.nodes().get("project_1")
        assert len(project.edges_in) == 1
        edge = project.edges_in[0]

        src = graph_classes.utils.get_edge_src(edge)
        assert src.node_id == "case_1"

        dst = graph_classes.utils.get_edge_dst(edge)
        assert dst.node_id == "project_1"


def test_exist_related_cases_from_cache_property(graph_classes: ModuleType) -> None:
    """Test exist _related_cases_from_cache property.

        Given a sample node
        When getting _related_cases_from_cache property
        Then we should get an empty list

    Args:
        graph_classes: all node and edges classes

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    assert sample._related_cases_from_cache == []


def test_exist_related_cases_from_parents_property(graph_classes: ModuleType) -> None:
    """Test exist _related_cases_from_parent property.

        Given a sample node
        When getting _related_cases_from_parent property
        Then we should get an empty list

    Args:
        graph_classes: all node and edges classes

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    assert sample._related_cases_from_parents == []
