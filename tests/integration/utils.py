import os

import psqlgraph


def get_graph_driver(namespace: str) -> psqlgraph.PsqlGraphDriver:
    return psqlgraph.PsqlGraphDriver(
        host=os.getenv("PG_HOST", "localhost"),
        password=os.getenv("PG_PASS", "test"),
        user=os.getenv("PG_USER", "test"),
        database=os.getenv("PG_NAME", "plaster"),
        package_namespace=namespace,
    )
