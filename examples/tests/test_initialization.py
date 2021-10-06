import psqlgraph

from examples import models


def test_init(pg_driver: psqlgraph.PsqlGraphDriver) -> None:
    with pg_driver.session_scope() as s:
        s.add(models.Program(node_id="p1", name="Test"))
        assert pg_driver.nodes(models.Program).count() == 1
