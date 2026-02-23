from types import ModuleType


def test_back_refs(graph_classes: ModuleType) -> None:
    project_class = graph_classes.Project
    assert project_class._pg_backrefs["cases"]["src_type"] == graph_classes.Case
    assert project_class._pg_backrefs["cases"]["name"] == "projects"


def test_pg_links(graph_classes: ModuleType) -> None:
    pg_links = graph_classes.Case._pg_links
    assert pg_links["projects"]["dst_type"] == graph_classes.Project
    assert pg_links["projects"]["edge_out"] == "_CaseMemberOfProject_out"


def test_pg_edges(graph_classes: ModuleType) -> None:
    pg_edges = graph_classes.Project._pg_edges
    assert pg_edges["programs"]["backref"] == "projects"
    assert pg_edges["programs"]["type"] == graph_classes.Program
    assert pg_edges["cases"]["backref"] == "projects"
    assert pg_edges["cases"]["type"] == graph_classes.Case


def test_id(graph_classes: ModuleType) -> None:
    case = graph_classes.Case(node_id="case_id")
    assert case.id == "case_id"
    case.id = "new_case_id"
    assert case.node_id == "new_case_id"


def test_relates_to_case_edges(graph_classes: ModuleType) -> None:
    edge = graph_classes.SampleRelatesToCase
    assert edge.__tablename__ == "edge_samplerelatestocase"
    assert edge.__label__ == "relates_to"
    assert edge.__dst_class__ == "Case"
    assert edge.__dst_table__ == "node_case"
    assert edge.__src_class__ == "Sample"
    assert edge.__src_table__ == "node_sample"

    assert edge.__dst_src_assoc__ == "_related_sample"
    assert edge.__src_dst_assoc__ == "_related_cases"
