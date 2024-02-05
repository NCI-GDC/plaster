from collections import namedtuple
from importlib import resources
from types import ModuleType
from typing import List

import psqlgml
import psqlgraph
import pytest
import yaml
from psqlgraph import ext, hydrator

from tests.integration import tear_down_graph, utils


@pytest.fixture(scope="module")
def sample_data(
    graph_classes_versioning: ModuleType, test_dictionary_versioning: psqlgml.Dictionary
) -> List[psqlgraph.Node]:
    with resources.as_file(resources.files("tests").joinpath("data/sample.yaml")) as f:
        graph = yaml.safe_load(f)

    raw_schemas = {key: value.raw for key, value in test_dictionary_versioning.schema.items()}
    RawDictionary = namedtuple("RawDictionary", "schema")
    raw_dictionary = RawDictionary(schema=raw_schemas)
    f = hydrator.GraphFactory(graph_classes_versioning, raw_dictionary)
    nodes = f.create_from_nodes_and_edges(
        nodes=graph["nodes"],
        edges=graph["edges"],
        unique_key="node_id",
        all_props=True,
    )

    return nodes


@pytest.fixture(scope="module")
def graph_driver_versioning(graph_classes_versioning: ModuleType) -> psqlgraph.PsqlGraphDriver:
    g = utils.get_graph_driver(graph_classes_versioning.namespace)
    base = ext.get_orm_base(graph_classes_versioning.namespace)
    psqlgraph.create_all(g.engine, base=base)
    yield g
    tear_down_graph(g)


EXPECTED_TAGS = {
    "be66197b-f6cc-4366-bded-365856ec4f63": "84044bd2-54a4-5837-b83d-f920eb97c18d",
    "a2b2d27a-6523-4ddd-8b2e-e94437a2aa23": "84044bd2-54a4-5837-b83d-f920eb97c18d",
    "813f97c4-dffc-4f94-b3f6-66a93476a233": "9a81bbad-b525-568c-b85d-d269a8bdc70a",
    "6974c692-be47-4cb8-b8d6-9bd815983cd9": "55814b2f-fc23-5bed-9eab-c73c52c105df",
    "5ffb4b0e-969e-4643-8187-536ce7130e9c": "55814b2f-fc23-5bed-9eab-c73c52c105df",
    "c6a795f6-ee4a-4fcd-bfed-79348e07cd49": "8cc95392-5861-5524-8b98-a85e18d8294c",
    "ed9aa864-1e40-4657-9378-7e3dc26551cc": "fddc5826-8853-5c1a-847d-5850d58ccb3e",
    "fb69d25b-5c5d-4879-8955-8f2126e57524": "293d5dd3-117c-5a0a-8030-a428fdf2681b",
}


def test_compute_tag(
    graph_classes_versioning: ModuleType, sample_data: List[psqlgraph.Node]
) -> None:
    """Tests version tags are computed correctly per node"""

    for node in sample_data:
        print(f"\n..........{node}...........")
        v_tag = graph_classes_versioning.versioning.compute_tag(node)
        assert v_tag == EXPECTED_TAGS[node.node_id], f"invalid tag computed for {node.node_id}"


@pytest.fixture(scope="module")
def create_samples(
    sample_data: List[psqlgraph.Node], graph_driver_versioning: ModuleType
) -> None:
    with graph_driver_versioning.session_scope() as s:
        version_2s = []
        for node in sample_data:
            # delay adding version 2
            if node.node_id in [
                "a2b2d27a-6523-4ddd-8b2e-e94437a2aa23",
                "5ffb4b0e-969e-4643-8187-536ce7130e9c",
            ]:
                version_2s.append(node)
                continue
            s.add(node)
        s.commit()
        for v2 in version_2s:
            s.add(v2)
    yield

    with graph_driver_versioning.session_scope():
        for n in sample_data:
            graph_driver_versioning.node_delete(n.node_id)


@pytest.mark.parametrize(
    "node_id, tag, version",
    [
        ("be66197b-f6cc-4366-bded-365856ec4f63", "84044bd2-54a4-5837-b83d-f920eb97c18d", 1),
        ("a2b2d27a-6523-4ddd-8b2e-e94437a2aa23", "84044bd2-54a4-5837-b83d-f920eb97c18d", 2),
        ("813f97c4-dffc-4f94-b3f6-66a93476a233", "9a81bbad-b525-568c-b85d-d269a8bdc70a", 1),
        ("6974c692-be47-4cb8-b8d6-9bd815983cd9", "55814b2f-fc23-5bed-9eab-c73c52c105df", 1),
        ("5ffb4b0e-969e-4643-8187-536ce7130e9c", "55814b2f-fc23-5bed-9eab-c73c52c105df", 2),
        ("c6a795f6-ee4a-4fcd-bfed-79348e07cd49", "8cc95392-5861-5524-8b98-a85e18d8294c", 1),
        ("ed9aa864-1e40-4657-9378-7e3dc26551cc", "fddc5826-8853-5c1a-847d-5850d58ccb3e", 1),
        ("fb69d25b-5c5d-4879-8955-8f2126e57524", "293d5dd3-117c-5a0a-8030-a428fdf2681b", 1),
    ],
)
def test_set_tag_after_insert_hook(
    create_samples: None,
    graph_driver_versioning: psqlgraph.PsqlGraphDriver,
    node_id: str,
    tag: str,
    version: int,
    graph_classes_versioning: ModuleType,
) -> None:
    """Test set tag after insert hook.

        Given a taggable node
        When the node is inserted into the database
        Then the set_tag_after_insert_hook should set tag, version value for the node

    Args:
        create_samples: fixture to create nodes for testing
        graph_driver_versioning: graph driver for the versioned graph (version_dict)
        node_id: node_id of node to check tag and version
        tag: tag number of the node
        version: version number of the node
        graph_classes_versioning: fixture of the versioned graph
    """

    with graph_driver_versioning.session_scope():
        node = graph_driver_versioning.nodes().get(node_id)
        assert node.tag == tag
        assert node.ver == version
        assert graph_classes_versioning.versioning.compute_tag(node) == node.tag


def test_multi_parent(
    sample_data: List[psqlgraph.Node], graph_classes_versioning: ModuleType
) -> None:
    """Test compute tag for multi parent

        Test version tag resolves to the same value independent of how the parents
        were attached.

        Given a portion node
        When no parents or parents removed
        Then it should have the same tag number.

        Given a portion node
        When same parents were attached
        Then the portion node should have the same tag number

    Args:
        sample_data: fixture to create test data
        graph_classes_versioning: fixture to create the versioned graph
    """
    portion = graph_classes_versioning.Portion(
        node_id="b9b6fdb3-6c31-4ed3-9f8c-67d4eae72102", submitter_id="portion_2"
    )
    v_tag = graph_classes_versioning.versioning.compute_tag(portion)
    assert v_tag == "5776f97a-a58b-5900-83da-43cbc7105796"

    sample = center = None
    for node in sample_data:
        if node.label == "center":
            center = node
        elif node.label == "sample":
            sample = node

    if not all([center, sample]):
        assert False

    portion.samples.append(sample)
    portion.centers.append(center)

    graph_classes_versioning.versioning.compute_tag.cache_clear()
    v_tag = graph_classes_versioning.versioning.compute_tag(portion)
    assert v_tag == "a9a67fae-d916-5843-bdf3-b7db0b7a82a2"

    # unlink
    portion.samples = []
    portion.centers = []

    graph_classes_versioning.versioning.compute_tag.cache_clear()
    v_tag = graph_classes_versioning.versioning.compute_tag(portion)
    assert v_tag == "5776f97a-a58b-5900-83da-43cbc7105796"

    portion.centers.append(center)
    portion.samples.append(sample)

    graph_classes_versioning.versioning.compute_tag.cache_clear()
    v_tag = graph_classes_versioning.versioning.compute_tag(portion)
    assert v_tag == "a9a67fae-d916-5843-bdf3-b7db0b7a82a2"
