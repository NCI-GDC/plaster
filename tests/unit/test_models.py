from os import PathLike
from pathlib import Path

import psqlgml

from plaster import generator


def test_source_file_generation(test_dictionary: psqlgml.Dictionary, tmpdir: PathLike) -> None:
    generator.generate(test_dictionary, str(tmpdir))

    assert Path(f"{tmpdir}/program.py").exists()
    assert Path(f"{tmpdir}/project.py").exists()
    assert Path(f"{tmpdir}/case.py").exists()
    assert Path(f"{tmpdir}/sample.py").exists()
