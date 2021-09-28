from plaster import models


# TOD0: clean up build folder after test
def test_generate(test_dictionary) -> None:
    models.generate(test_dictionary)
