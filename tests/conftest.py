import pkg_resources
import pytest
from psqlgml import dictionary

from plaster import config


@pytest.fixture(scope="session")
def app_settings() -> str:
    return pkg_resources.resource_filename("tests", "data/plaster.toml")


@pytest.fixture()
def plaster_config(app_settings) -> config.PlasterConfig:
    yield config.load_config(app_settings)


@pytest.fixture()
def test_dictionary(plaster_config) -> dictionary.Dictionary:
    dict_dir = pkg_resources.resource_filename("tests", "data")
    return dictionary.load_local(version="0.1.0", name="dictionary", dictionary_location=dict_dir)
