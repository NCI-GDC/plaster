import pkg_resources
import pytest


@pytest.fixture(scope="session")
def app_settings() -> str:
    return pkg_resources.resource_filename("tests", "data/plaster.toml")
