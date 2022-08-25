import psqlgml


def test_dictionary_loading(test_dictionary: psqlgml.Dictionary) -> None:
    assert test_dictionary.schema
    assert len(test_dictionary.schema) == 7
    program = test_dictionary.schema["program"]

    assert program.id == "program"
    assert program.category == "administrative"
    assert program.downloadable is False
    assert program.required


def test_case_loading(test_dictionary: psqlgml.Dictionary) -> None:
    case = test_dictionary.schema["case"]

    assert case.id == "case"
    assert case.category == "administrative"
    assert case.downloadable is False
    assert case.required


def test_project_loading(test_dictionary: psqlgml.Dictionary) -> None:
    project = test_dictionary.schema["project"]

    assert project.id == "project"
    assert project.category == "administrative"
    assert project.downloadable is False


def test_sample_loading(test_dictionary: psqlgml.Dictionary) -> None:
    sample = test_dictionary.schema["sample"]

    assert sample.id == "sample"
    assert sample.category == "biospecimen"
    assert sample.downloadable is False
