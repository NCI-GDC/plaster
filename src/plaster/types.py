from typing import TypedDict


class PgLinksDict(TypedDict):
    edges_out: str
    dst_type: str


class PgBackRefDict(TypedDict):
    name: str
    src_type: str


class PgEdgeDict(TypedDict):
    backref: str
    type: str
