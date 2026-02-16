from types import ModuleType

import pytest


def test_tag(graph_classes_versioning: ModuleType) -> None:
    """Test AliquotLevelMaf has tag

    Given an AliquotLevelMaf node with tagProperties in its schema
    When its _sysan["tag"] is set to tag_1
    Then it should have a tag property
    And its tag property should return tag_1

    Args:
        graph_classes_versioning:  all node and edge classes.
    """
    AliquotLevelMaf = graph_classes_versioning.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "tag")

    aliquot_level_maf = AliquotLevelMaf("aliquot_level_maf_1")
    assert aliquot_level_maf.tag is None
    aliquot_level_maf._sysan["tag"] = "tag_1"
    assert aliquot_level_maf.tag == "tag_1"


def test_no_tag(graph_classes: ModuleType) -> None:
    """Test case node should not have tag

    Given a case node without tagProperties in its schema
    Then it should not have tag prooperty.

    Args:
        graph_classes:
    """
    Case = graph_classes.Case
    assert not hasattr(Case, "tag")


def test_ver(graph_classes_versioning: ModuleType) -> None:
    """Test AliquotLevelMaf has version

    Given an AliquotLevelMaf node with tagProperties in its schema
    When its _sysan["ver"] is set to 1
    Then it should have a ver property
    And its ver property should return 1

    Args:
        graph_classes_versioning:  all nodes and edges classes.
    """
    AliquotLevelMaf = graph_classes_versioning.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "ver")

    aliquot_level_maf = AliquotLevelMaf("aliquot_level_maf_1")
    assert aliquot_level_maf.ver is None
    aliquot_level_maf._sysan["ver"] = 1
    assert aliquot_level_maf.ver == 1


def test_tag_properties(graph_classes_versioning: ModuleType) -> None:
    """Test teg properties

    Args:
        graph_classes_versioning: all nodes and edges classes
    """
    AliquotLevelMaf = graph_classes_versioning.AliquotLevelMaf
    assert AliquotLevelMaf.tag_properties == ["data_type"]


def test_is_latest(graph_classes_versioning: ModuleType) -> None:
    """test is latest property

    Args:
        graph_classes_versioning:  all nodes and edges classes
    """
    AliquotLevelMaf = graph_classes_versioning.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "is_latest")

    aliquot_level_maf = AliquotLevelMaf("aliquot_level_maf_1")
    assert aliquot_level_maf.is_latest is False
    aliquot_level_maf._sysan["latest"] = True
    assert aliquot_level_maf.is_latest is True


def test_is_taggable__no_path(graph_classes_versioning: ModuleType) -> None:
    """Test is taggable with no path in tag config

        Given a Vcf2mafWorkflow node
        When is_taggable method is called
        Then it should return True iff the workflow type is not SomaticSniper

    Args:
        graph_classes_versioning: all nodes and edges classes
    """
    Vcf2mafWorkflow = graph_classes_versioning.Vcf2mafWorkflow
    assert hasattr(Vcf2mafWorkflow, "tag_builder_config")

    vcf_2_maf_workflow = Vcf2mafWorkflow("vcf_2_maf_workflow_1")
    assert vcf_2_maf_workflow.is_taggable() is True

    vcf_2_maf_workflow.workflow_type = "SomaticSniper"
    assert vcf_2_maf_workflow.is_taggable() is False


def test_is_taggable__with_path(graph_classes_versioning: ModuleType) -> None:
    """Test is taggable with path in tag config

        Given an AliquotLevelMaf node
        When is_taggable method is called
        Then it should return True iff its parent Vcf2mafWorkflow type is not SomaticSniper

    Args:
        graph_classes_versioning: all nodes and edges classes
    """
    AliquotLevelMaf = graph_classes_versioning.AliquotLevelMaf
    assert hasattr(AliquotLevelMaf, "tag_builder_config")

    vcf_2_maf_workflow = graph_classes_versioning.Vcf2mafWorkflow(
        "vcf_2_maf_workflow_1"
    )
    vcf_2_maf_workflow.workflow_type = "SomaticSniper"

    aliquot_level_maf = AliquotLevelMaf("aliquot_level_maf_1")
    assert aliquot_level_maf.is_taggable() is True
    aliquot_level_maf["vcf2maf_workflows"] = [vcf_2_maf_workflow]
    assert aliquot_level_maf.is_taggable() is False


def test_get_tag_property_values(graph_classes_versioning: ModuleType) -> None:
    aliquot_level_maf = graph_classes_versioning.AliquotLevelMaf("aliquot_level_maf_1")
    aliquot_level_maf.data_type = "Aliquot Level MAF"
    assert aliquot_level_maf.get_tag_property_values() == ["Aliquot Level MAF"]


def test_get_tag_property_values__raise_for_missing_value(
    graph_classes_versioning: ModuleType,
) -> None:
    aliquot_level_maf = graph_classes_versioning.AliquotLevelMaf("aliquot_level_maf_1")
    with pytest.raises(ValueError):
        aliquot_level_maf.get_tag_property_values()
