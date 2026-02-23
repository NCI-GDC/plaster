from types import ModuleType

import psqlgraph
from deepdiff import DeepDiff


def test_pg_secondary_keys(graph_classes: ModuleType) -> None:
    case_cls = graph_classes.Case
    # python default mangled name we are not supposed to be using
    assert DeepDiff(case_cls._Case__pg_secondary_keys, [["project_id", "submitter_id"]]) == {}
    assert DeepDiff(case_cls.pg_secondary_keys(), [["project_id", "submitter_id"]]) == {}


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


def test_secondary_keys_indexes(graph_classes: ModuleType) -> None:
    case_cls = graph_classes.Case
    index_names = {i.name for i in case_cls.__table__.indexes}
    expected = {
        "index_node_case_submitter_id",
        "index_node_case_project_id",
        "index_node_case_project_id_lower",
        "index_node_case_submitter_id_lower",
    }
    assert expected - index_names == set()


def test_secondary_keys_comparator(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys
        Then case node with right values for secondary keys should be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case = case_cls("case_1")
        case.project_id = "project_1"
        case.submitter_id = "submitter_1"
        s.add(case)
        s.commit()

        secondary_keys = (("project_1", "submitter_1"),)

        case = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .one_or_none()
        )
        assert case.node_id == "case_1"


def test_secondary_keys_comparator_wrong_values_return_none(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys
        Then case node with different values for secondary keys should not be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case = case_cls("case_1")
        case.project_id = "project_1"
        case.submitter_id = "submitter_1"
        s.add(case)
        s.commit()

        secondary_keys = (("project_1", "wrong_id"),)

        case = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .one_or_none()
        )
        assert case is None


def test_secondary_keys_comparator__match_when_first_value_match(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys for single value
        Then case node with first value match should be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case = case_cls("case_1")
        case.project_id = "project_1"
        case.submitter_id = "submitter_1"
        s.add(case)
        s.commit()

        secondary_keys = (("project_1",),)

        case = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .one_or_none()
        )
        assert case.node_id == "case_1"


def test_secondary_keys_comparator__miss_when_second_value_match(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys for single value
        Then case node with second value match should not be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case = case_cls("case_1")
        case.project_id = "project_1"
        case.submitter_id = "submitter_1"
        s.add(case)
        s.commit()

        secondary_keys = (("submitter_1",),)

        case = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .one_or_none()
        )
        assert case is None


def test_secondary_keys_comparator__match_when_empty_search_value(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys for empty value
        Then all case nodes should be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case1 = case_cls("case_1")
        case1.project_id = "project_1"
        case1.submitter_id = "submitter_1"
        case2 = case_cls("case_2")
        case2.project_id = "project_2"
        case3 = case_cls("case_3")
        case3.submitter_id = "submitter_3"
        case4 = case_cls("case_4")

        s.add_all([case1, case2, case3, case4])
        s.commit()

        secondary_keys = ((),)

        cases = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .all()
        )
        assert len(cases) == 4


def test_secondary_keys_comparator__match_with_extra_value(
    graph_classes: ModuleType, graph_driver: psqlgraph.PsqlGraphDriver
) -> None:
    """Test secondary keys comparator

        Given a saved case node
        When filter with secondary keys containing extra value
        Then case node with right values for first 2 values should be returned

    Args:
        graph_classes: all node and edge classes
        graph_driver: psqlgraph driver

    Returns:
        None
    """
    with graph_driver.session_scope() as s:
        case_cls = graph_classes.Case
        case = case_cls("case_1")
        case.project_id = "project_1"
        case.submitter_id = "submitter_1"
        s.add(case)
        s.commit()

        secondary_keys = (("project_1", "submitter_1", "any_1"),)

        case = (
            graph_driver.nodes(case_cls)
            .filter(case_cls._secondary_keys == secondary_keys)
            .one_or_none()
        )
        assert case.node_id == "case_1"
