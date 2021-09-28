import pytest
from click.testing import CliRunner
from psqlgml import dictionary


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_dict() -> dictionary.Dictionary:
    return dictionary.load(version="2.4.1")
