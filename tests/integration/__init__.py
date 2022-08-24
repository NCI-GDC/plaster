import warnings

import psqlgraph
from sqlalchemy import MetaData, engine
from sqlalchemy import exc as sa_exc

from src.plaster.templates import versioned_nodes


def tear_down_graph(graph: psqlgraph.PsqlGraphDriver) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)

        m = MetaData(graph.engine)
        m.reflect()
        for tbl in reversed(m.sorted_tables):
            graph.engine.execute(tbl.delete())

        # close connection to database
        graph.engine.dispose()


def create_versioned_nodes_tables(graph_engine: engine.Engine):
    versioned_nodes.Base.metadata.create_all(graph_engine)


def truncate_versioned_nodes_tables(graph_engine: engine.Engine):
    conn = graph_engine.connect()
    for table in versioned_nodes.Base.metadata.tables:
        conn.execute(f"DELETE FROM {table}")  # nosec
