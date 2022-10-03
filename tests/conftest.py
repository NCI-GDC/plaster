import pkg_resources
import psqlgml
import pytest

from plaster import config


@pytest.fixture(scope="session")
def app_settings() -> str:
    return pkg_resources.resource_filename("tests", "plaster-test.toml")


@pytest.fixture(scope="session")
def plaster_config(app_settings: str) -> config.PlasterConfig:
    yield config.load_config(app_settings)


@pytest.fixture(scope="session")
def test_dictionary(plaster_config: config.PlasterConfig) -> psqlgml.Dictionary:
    dict_dir = pkg_resources.resource_filename("tests", "data")
    return psqlgml.load_local(version="0.1.0", name="dictionary", dictionary_location=dict_dir)
