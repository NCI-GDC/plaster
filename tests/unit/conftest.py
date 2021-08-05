import os
from unittest import mock

import pytest
from py.path import local

from plaster import config


@pytest.fixture()
def plaster_config(app_settings, tmpdir: local) -> config.PlasterConfig:
    with mock.patch.dict(os.environ, {"PLASTER_GIT_HOME": f"{tmpdir}/.plaster/git"}):
        yield config.load_config(app_settings)
