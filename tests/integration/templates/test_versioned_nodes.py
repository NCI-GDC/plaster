from types import ModuleType

import psqlgraph
import pytest

from plaster.templates import versioned_nodes


@pytest.fixture
def portion(graph_classes: ModuleType):
    portion = graph_classes.Portion(
        **{
            "node_id": "case1",
            "is_ffpe": False,
            "portion_number": "01",
            "project_id": "CGCI-BLGSP",
            "state": "validated",
            "submitter_id": "PORTION-1",
            "weight": 54.0,
        }
    )
    portion.acl = ["acl1"]
    portion.sysan.update({"key1": "val1"})
    return portion


@pytest.fixture
def analyte(graph_classes: ModuleType):
    return graph_classes.Analyte(
        **{
            "node_id": "analyte1",
            "analyte_type": "Repli-G (Qiagen) DNA",
            "analyte_type_id": "W",
            "project_id": "CGCI-BLGSP",
            "state": "validated",
            "submitter_id": "TCGA-AR-A1AR-01A-31W",
        }
    )


def test_round_trip(
    graph_driver: psqlgraph.PsqlGraphDriver,
    portion: psqlgraph.Node,
    analyte: psqlgraph.Node,
    graph_classes: ModuleType,
):
    with graph_driver.session_scope() as session:
        portion.analytes = [analyte]
        session.add(portion)

    with graph_driver.session_scope() as session:
        portion = graph_driver.nodes(graph_classes.Portion).one()
        v_node = versioned_nodes.VersionedNode.clone(portion)
        session.add(v_node)

    with graph_driver.session_scope():
        v_node = graph_driver.nodes(versioned_nodes.VersionedNode).one()

    assert v_node.properties["is_ffpe"] is False
    assert v_node.properties["state"] == "validated"
    assert v_node.system_annotations == {"key1": "val1"}
    assert v_node.acl == ["acl1"]
    assert v_node.neighbors == ["analyte1"]
    assert v_node.versioned is not None
    assert v_node.key is not None


@pytest.mark.skip(reason="_version not implemented")
def test_versions_property(
    gdc_graph: psqlgraph.PsqlGraphDriver,
    portion: psqlgraph.Node,
    analyte: psqlgraph.Node,
    graph_classes: ModuleType,
):
    with gdc_graph.session_scope() as session:
        portion.analytes = [analyte]
        session.add(portion)

    with gdc_graph.session_scope() as session:
        portion = gdc_graph.nodes(graph_classes.Portion).one()
        v_node = versioned_nodes.VersionedNode.clone(portion)
        session.add(v_node)

    with gdc_graph.session_scope():
        portion = gdc_graph.nodes(graph_classes.Portion).one()
        portion._versions.one()

    with pytest.raises(RuntimeError):
        portion._versions.one()

    with gdc_graph.session_scope() as s:
        portion.get_versions(s).one()
