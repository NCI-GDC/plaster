import warnings

import psqlgraph
from sqlalchemy import MetaData
from sqlalchemy import exc as sa_exc


def tear_down_graph(graph: psqlgraph.PsqlGraphDriver) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)

        m = MetaData(graph.engine)
        m.reflect()
        for tbl in reversed(m.sorted_tables):
            graph.engine.execute(tbl.delete())

        # close connection to database
        graph.engine.dispose()
