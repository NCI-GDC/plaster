import psqlgml


def test_dictionary_loading(test_dict: psqlgml.Dictionary) -> None:
    assert test_dict.schema
    assert len(test_dict.schema) == 81
