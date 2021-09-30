from os import PathLike
from pathlib import Path

import psqlgml
from _pytest.monkeypatch import MonkeyPatch

from plaster import generator


def test_generate(
    test_dictionary: psqlgml.Dictionary, tmpdir: PathLike, monkeypatch: MonkeyPatch
) -> None:

    monkeypatch.setattr(generator, "OUTPUT_LOCATION", str(tmpdir))
    generator.generate(test_dictionary)

    assert Path(f"{tmpdir}/program.py").exists()
    assert Path(f"{tmpdir}/project.py").exists()
    assert Path(f"{tmpdir}/case.py").exists()
