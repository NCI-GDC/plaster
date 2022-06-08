from typing import NamedTuple


class PgLink(NamedTuple):
    edges_out: str
    dst_type: str


class PgBackRef(NamedTuple):
    name: str
    src_type: str


class PgEdge(NamedTuple):
    backref: str
    type: str
