from psqlgml import dictionary


def test_dictionary_loading(test_dict) -> None:
    assert test_dict.schema
    assert len(test_dict.schema) == 3
