import os
from pathlib import Path
from unittest import mock

import pytest

from plaster import repository

REMOTE_GIT_URL = "https://github.com/NCI-GDC/gdcdictionary.git"


def test_init_with_home() -> None:
    rm = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
    assert rm.git_dir == f"{Path.home()}/.plaster/git/smiths"


def test_init_repo_meta(tmpdir) -> None:

    with mock.patch.dict(os.environ, {"PLASTER_GIT_HOME": f"{tmpdir}/.plaster/git"}):
        rm = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
        assert rm.git_dir == f"{tmpdir}/.plaster/git/smiths"
        assert rm.is_cloned is False


@pytest.mark.usefixtures("plaster_config")
def test_clone_repo() -> None:
    rm = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
    r = repository.clone(rm)
    assert rm.is_cloned
    assert r.head()


def test_get_checkout_dir() -> None:
    chk_dir = repository.get_checkout_dir(commit_sha=b"sss")
    assert chk_dir == f"{Path.home()}/.plaster/checkouts/sss"


@pytest.mark.usefixtures("plaster_config")
def test_get_commit_id() -> None:
    rm = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
    repo = repository.clone(rm)

    commands = {
        b"f7ba557228bc113c92387c4eb6160621d27b53ef": repository.RepoCheckout(
            repo=rm, path="", commit="2.4.0"
        ),
        b"1595aef2484ab6fa6c945950b296c4031c2606fd": repository.RepoCheckout(
            repo=rm, path="", commit="2.3.0"
        ),
        b"7107e8116ce6ed8185626570dcba14b46e8e4d27": repository.RepoCheckout(
            repo=rm, path="", commit="release/avery", is_tag=False
        ),
    }
    for sha, command in commands.items():
        assert sha == repository.get_commit_id(repo, command.ref)


@pytest.mark.usefixtures("plaster_config")
def test_checkout() -> None:
    repo = repository.RepoMeta(remote_git_url=REMOTE_GIT_URL, name="smiths")
    command = repository.RepoCheckout(repo=repo, path="gdcdictionary/schemas", commit="2.3.0")

    chk_dir = Path(repository.checkout(repo, command))
    assert chk_dir.exists()

    entries = [f.name for f in chk_dir.iterdir()]
    assert "program.yaml" in entries
