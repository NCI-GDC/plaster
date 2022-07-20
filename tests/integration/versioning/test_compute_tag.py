from collections import namedtuple
from types import ModuleType
from typing import List

import pkg_resources
import psqlgml
import psqlgraph
import pytest
import yaml
from psqlgraph import mocks


@pytest.fixture(scope="module")
def sample_data(
    graph_classes_versioning: ModuleType, test_dictionary_versioning: psqlgml.Dictionary
) -> List[psqlgraph.Node]:
    with pkg_resources.resource_stream("tests", "data/sample.yaml") as f:
        graph = yaml.safe_load(f)

    raw_schemas = {key: value.raw for key, value in test_dictionary_versioning.schema.items()}
    RawDictionary = namedtuple("RawDictionary", "schema")
    raw_dictionary = RawDictionary(schema=raw_schemas)
    f = mocks.GraphFactory(graph_classes_versioning, raw_dictionary)
    nodes = f.create_from_nodes_and_edges(
        nodes=graph["nodes"],
        edges=graph["edges"],
        unique_key="node_id",
        all_props=True,
    )

    return nodes


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
