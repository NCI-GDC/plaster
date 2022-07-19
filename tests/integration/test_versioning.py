from types import ModuleType


def test_tag(graph_classes: ModuleType) -> None:
    """Test AliquotLevelMaf has tag

    Given an AliquotLevelMaf node with tagProperties in its schema
    When its _sysan["tag"] is set to tag_1
    Then it should have a tag property
    And its tag property should return tag_1

    Args:
        graph_classes:  all node and edge classes.

    Returns:
        None
    """
    AliquotLevelMaf = graph_classes.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "tag")

    alm = AliquotLevelMaf("alm_1")
    assert alm.tag is None
    alm._sysan["tag"] = "tag_1"
    assert alm.tag == "tag_1"


def test_no_tag(graph_classes: ModuleType) -> None:
    """Test case node should not have tag

    Given a case node without tagProperties in its schema
    Then it should not have tag prooperty.

    Args:
        graph_classes:

    Returns:
        None
    """
    Case = graph_classes.Case
    assert not hasattr(Case, "tag")


def test_ver(graph_classes: ModuleType) -> None:
    """Test AliquotLevelMaf has version

    Given an AliquotLevelMaf node with tagProperties in its schema
    When its _sysan["ver"] is set to 1
    Then it should have a ver property
    And its ver property should return 1

    Args:
        graph_classes:  all node and edge classes.

    Returns:
        None
    """
    AliquotLevelMaf = graph_classes.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "ver")

    alm = AliquotLevelMaf("alm_1")
    assert alm.ver is None
    alm._sysan["ver"] = 1
    assert alm.ver == 1
