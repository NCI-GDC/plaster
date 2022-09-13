from types import ModuleType


def test_file_pg_edges(graph_classes: ModuleType) -> None:
    """Test file pg edges.

        Given a file node
        When different type of edges exists between
            1. the file nodes and case nodes
            2. the file nodes and other file nodes
        Then _pg_edges should have the correct link information.

    Args:
        graph_classes: All node and edge classes
    """
    # from pg links
    assert graph_classes.File._pg_edges["cases"] == {
        "backref": "files",
        "type": graph_classes.Case,
    }

    assert graph_classes.File._pg_edges["described_cases"] == {
        "backref": "describing_files",
        "type": graph_classes.Case,
    }

    assert graph_classes.File._pg_edges["source_files"] == {
        "backref": "derived_files",
        "type": graph_classes.File,
    }

    assert graph_classes.File._pg_edges["related_files"] == {
        "backref": "parent_files",
        "type": graph_classes.File,
    }

    # from pg backrefs
    assert graph_classes.File._pg_edges["derived_files"] == {
        "backref": "source_files",
        "type": graph_classes.File,
    }

    assert graph_classes.File._pg_edges["parent_files"] == {
        "backref": "related_files",
        "type": graph_classes.File,
    }
