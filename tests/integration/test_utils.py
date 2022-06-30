import sys
from pathlib import Path

from click.testing import CliRunner

from plaster import cli


def test_get_related_case_edge_cls_name(
    cli_runner: CliRunner, app_settings: str, tmpdir: Path
) -> None:
    result = cli_runner.invoke(
        cli.app,
        ["-c", app_settings, "generate", "-p", "dictionary", "-o", tmpdir / "test_module"],
    )
    assert result.exit_code == 0

    sys.path.insert(0, str(tmpdir))
    import test_module
    from test_module import utils

    sample = test_module.Sample("sample_1")

    edge_name = utils.get_related_case_edge_cls_name(sample)

    assert edge_name == "SampleRelatesToCase"
