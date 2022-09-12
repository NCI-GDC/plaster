from types import ModuleType


def test_case_node_table_args_extend_existing_is_true(graph_classes: ModuleType) -> None:
    assert graph_classes.Case.__table_args__["extend_existing"] is True
