from types import ModuleType

import psqlgraph


def test_get_related_case_edge_cls_name(graph_classes: ModuleType) -> None:
    sample = graph_classes.Sample("sample_1")

    edge_name = graph_classes.utils.get_related_case_edge_cls_name(sample)

    assert edge_name == "SampleRelatesToCase"
