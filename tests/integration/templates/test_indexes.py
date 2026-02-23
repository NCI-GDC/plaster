from types import ModuleType


def test_create_index_name_short_name(graph_classes: ModuleType) -> None:
    """Test create long index name.

        Given a node class and a short description
        When index name is called
        Then we should get a truncated index name with hex value in it

    Args:
        graph_classes: all node and edge classes
    """
    case_cls = graph_classes.Case
    description = "submitter_id"

    index_name = graph_classes.indexes.index_name(case_cls, description)

    assert index_name == "index_node_case_submitter_id"


def test_create_index_name_long_name(graph_classes: ModuleType) -> None:
    """Test create long index name.

        Given a node class and a long description(or long class name)
        When index name is called
        Then we should get a truncated index name with hex value in it

    Args:
        graph_classes: all node and edge classes
    """
    case_cls = graph_classes.Case
    description = "veryveryveryveryveryveryveryverylongdescription"

    index_name = graph_classes.indexes.index_name(case_cls, description)

    assert index_name == "index_2271f5c5_case_veryvery"
