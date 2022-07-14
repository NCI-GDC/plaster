from types import ModuleType

import psqlgraph
from deepdiff import DeepDiff


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


def test_get_edge_src(graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver) -> None:
    """test get edge src.

        Given an edge between 2 nodes
        When get_edge_src is called
        Then the source node should be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

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


def test_get_edge_dst(graph_driver: psqlgraph.PsqlGraphDriver, graph_classes: ModuleType) -> None:
    """test get edge dst.

        Given an edge between 2 nodes
        When get_edge_dst is called
        Then the destination node should be returned

    Args:
        graph_driver: psqlgraph driver
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

        dst = graph_classes.utils.get_edge_dst(edge)
        assert dst.node_id == "project_1"


def test_exist_related_cases_from_cache_property(graph_classes: ModuleType) -> None:
    """Test exist _related_cases_from_cache property.

        Given a sample node without any parent node
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

        Given a sample node without any parent node
        When getting _related_cases_from_parent property
        Then we should get an empty list

    Args:
        graph_classes: all node and edges classes

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    assert sample._related_cases_from_parents == []


def test_update_cac_edges(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """test update cache edges.

        Given a sample node and a dictionary of correct_cases
        When update_cache_edges called
        Then remove cases not in correct_cases from sample node's _related_cases
        And add missing edges from correct_cases to sample node's _related_cases

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    case1 = graph_classes.Case("case_1")
    case2 = graph_classes.Case("case_2")
    case3 = graph_classes.Case("case_3")
    case4 = graph_classes.Case("case_4")

    with graph_driver.session_scope() as s:
        s.merge(sample)

        sample = graph_driver.nodes().get("sample_1")
        sample._related_cases.extend([case1, case2, case3])

        parent_cases = [case2, case3, case4]
        correct_cases = {c.node_id: c for c in parent_cases}

        graph_classes.utils.update_cache_edges(sample, correct_cases)
        assert set(sample._related_cases) == {case2, case3, case4}


def test_cache_related_cases_recursive(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test cache_related_cases_recursive function.

        Given a sample node and a child aliquot node added to session
        When cache_related_cases_recursive called with sample node
        Then the _related_cases should be updated for the sample and aliquot nodes

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    case1 = graph_classes.Case("case_1")
    case2 = graph_classes.Case("case_2")
    aliquot = graph_classes.Aliquot("aliquot_1")

    with graph_driver.session_scope() as s:
        sample.cases = [case1, case2]
        sample.aliquots = [aliquot]
        s.add(sample)

        graph_classes.utils.cache_related_cases_recursive(sample)
        assert len(sample._related_cases) == 2
        sample_related_case_ids = [n.node_id for n in sample._related_cases]
        aliquot_related_case_ids = [n.node_id for n in aliquot._related_cases]
        expected = ["case_1", "case_2"]
        assert DeepDiff(sample_related_case_ids, expected, ignore_order=True) == {}
        assert DeepDiff(aliquot_related_case_ids, expected, ignore_order=True) == {}


def test_cache_related_cases_recursive__update_when_cases_changes(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test cache_related_cases_recursive function update _related_cases.

        Given a sample node and a child aliquot node added to session
        When ancestor cases changed
        And cache_related_cases_recursive called with sample node
        Then the _related_cases should be updated for the sample and aliquot nodes

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    case1 = graph_classes.Case("case_1")
    case2 = graph_classes.Case("case_2")
    case3 = graph_classes.Case("case_3")
    aliquot = graph_classes.Aliquot("aliquot_1")

    with graph_driver.session_scope() as s:
        sample.cases = [case1, case2]
        sample.aliquots = [aliquot]
        s.add(sample)

        graph_classes.utils.cache_related_cases_recursive(sample)

        sample.cases = [case1, case3]
        s.merge(sample)
        graph_classes.utils.cache_related_cases_recursive(sample)
        assert len(sample._related_cases) == 2
        sample_related_case_ids = [n.node_id for n in sample._related_cases]
        aliquot_related_case_ids = [n.node_id for n in aliquot._related_cases]
        expected = ["case_1", "case_3"]
        assert DeepDiff(sample_related_case_ids, expected, ignore_order=True) == {}
        assert DeepDiff(aliquot_related_case_ids, expected, ignore_order=True) == {}


def test_related_case_hook_before_insert(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test related case hook before insert

        Given a sample node and a child aliquot node with cases ancestors
        When a new edge is added
        Then the _related_cases should be updated for the aliquot nodes

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    sample = graph_classes.Sample("sample_1")
    case1 = graph_classes.Case("case_1")
    case2 = graph_classes.Case("case_2")
    aliquot = graph_classes.Aliquot("aliquot_1")

    with graph_driver.session_scope() as s:
        sample.cases = [case1, case2]
        sample.aliquots = [aliquot]
        s.add(sample)
        s.commit()

        aliquot_related_case_ids = [n.node_id for n in aliquot._related_cases]
        expected = ["case_1", "case_2"]
        assert DeepDiff(aliquot_related_case_ids, expected, ignore_order=True) == {}
