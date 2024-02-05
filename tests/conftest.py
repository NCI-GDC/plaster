from os import path

import psqlgml
import pytest

from plaster import config


@pytest.fixture(scope="session")
def app_settings() -> str:
    current_dir = path.abspath(path.dirname(__file__))
    return path.join(current_dir, "plaster-test.toml")


@pytest.fixture(scope="session")
def plaster_config(app_settings: str) -> config.PlasterConfig:
    yield config.load_config(app_settings)


@pytest.fixture(scope="session")
def test_data_location() -> str:
    current_dir = path.abspath(path.dirname(__file__))
    return path.join(current_dir, "data")


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("plaster_config")
def test_dictionary(test_data_location) -> psqlgml.Dictionary:
    return psqlgml.load_local(
        version="0.1.0", name="dictionary", dictionary_location=test_data_location
    )
