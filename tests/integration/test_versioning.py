from types import ModuleType


def test_tag(graph_classes: ModuleType) -> None:
    Case = graph_classes.Case
    assert not hasattr(Case, "tag")

    AliquotLevelMaf = graph_classes.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "tag")

    alm = AliquotLevelMaf("alm_1")
    alm._sysan["tag"] = "tag_1"
    assert alm.tag == "tag_1"
