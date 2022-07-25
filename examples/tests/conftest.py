import os
from typing import Dict

import pkg_resources
import psqlgml
import pytest
from pytest_psqlgraph.models import DatabaseDriverConfig

from examples import models


@pytest.fixture(scope="session")
def test_dictionary() -> psqlgml.Dictionary:
    dict_dir = pkg_resources.resource_filename("tests", "data")
    return psqlgml.load_local(version="0.1.0", name="dictionary", dictionary_location=dict_dir)


@pytest.fixture(scope="session")
def psqlgraph_config(test_dictionary: psqlgml.Dictionary) -> Dict[str, DatabaseDriverConfig]:
    return {
        "pg_driver": DatabaseDriverConfig(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            model=models,
            dictionary=test_dictionary,
        )
    }
