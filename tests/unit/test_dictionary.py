from pathlib import Path

import pkg_resources
import pytest

from plaster import dictionary, repository

REMOTE_GIT_URL = "https://github.com/NCI-GDC/gdcdictionary.git"


@pytest.fixture()
def dictionary_dir(plaster_config) -> Path:
    repo = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
    command = repository.RepoCheckout(repo=repo, path="gdcdictionary/schemas", commit="2.3.0")

    chk_dir = Path(repository.checkout(repo, command))
    assert chk_dir.exists()
    return chk_dir


@pytest.fixture()
def sample_dictionary(plaster_config) -> dictionary.Dictionary:
    dict_dir = pkg_resources.resource_filename("tests", "data/dictionary")
    return dictionary.load(schema_dir=dict_dir)


def test_dictionary_loading(dictionary_dir: Path) -> None:
    d1 = dictionary.load(schema_dir=str(dictionary_dir))
    assert d1.schema
    assert len(d1.schema) == 81
    program = d1.schema["program"]
    assert program.category == "administrative"
    assert program.downloadable is False


def test_schema_resolution() -> None:
    dict_dir = pkg_resources.resource_filename("tests", "data/dictionary")
    dd = dictionary.load(schema_dir=dict_dir)
    assert dd.schema
