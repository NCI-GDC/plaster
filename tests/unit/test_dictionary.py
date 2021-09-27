import psqlgml


def test_dictionary_loading(test_dictionary: psqlgml.Dictionary) -> None:
    assert test_dictionary.schema
    assert len(test_dictionary.schema) == 3
    program = test_dictionary.schema["program"]

    assert program.id == "program"
    assert program.category == "administrative"
    assert program.downloadable is False
    assert program.required
