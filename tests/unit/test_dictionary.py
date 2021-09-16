from psqlgml import dictionary


def test_dictionary_loading(test_dictionary: dictionary.Dictionary) -> None:
    assert test_dictionary.schema
    assert len(test_dictionary.schema) == 3
    program = test_dictionary.schema["program"]

    assert program.id == "program"
    assert program.category == "administrative"
    assert program.downloadable is False
    assert program.required


def test_case_loading(test_dictionary: dictionary.Dictionary) -> None:
    case = test_dictionary.schema["case"]

    assert case.id == "case"
    assert case.category == "administrative"
    assert case.downloadable is False
    assert case.required


def test_project_loading(test_dictionary: dictionary.Dictionary) -> None:
    project = test_dictionary.schema["project"]

    assert project.id == "project"
    assert project.category == "administrative"
    assert project.downloadable is False


if __name__ == "__main__":
    test_dictionary_loading(dictionary.Dictionary)
    test_case_loading(dictionary.Dictionary)
    test_project_loading(dictionary.Dictionary)
    print("Everything passed")
