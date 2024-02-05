from importlib import resources
from os import PathLike

import psqlgml
import pytest

from plaster import config


@pytest.fixture(scope="session")
def app_settings() -> PathLike:
    with resources.as_file(resources.files("tests").joinpath("plaster-test.toml")) as p:
        yield p


@pytest.fixture(scope="session")
def plaster_config(app_settings: PathLike) -> config.PlasterConfig:
    yield config.load_config(app_settings)


@pytest.fixture(scope="session")
def test_data_location() -> PathLike:
    with resources.as_file(resources.files("tests").joinpath("data")) as p:
        yield p


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("plaster_config")
def test_dictionary(test_data_location) -> psqlgml.Dictionary:
    return psqlgml.load_local(
        version="0.1.0", name="dictionary", dictionary_location=test_data_location
    )
