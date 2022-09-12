from types import ModuleType


def test_sample_derived_from_case_edge_table_args_extend_existing_is_true(
    graph_classes: ModuleType,
) -> None:
    assert graph_classes.SampleDerivedFromCase.__table_args__["extend_existing"] is True
