import psqlgml
import pytest
from click.testing import CliRunner


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_dict() -> psqlgml.Dictionary:
    return psqlgml.load(version="2.4.0")
