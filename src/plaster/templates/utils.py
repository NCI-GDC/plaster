from typing import Any, Iterable, List, Optional

import psqlgraph
import sqlalchemy
from psqlgraph import ext
from sqlalchemy.ext import hybrid

# the register_base_class is needed for edge.get_node_class to work
ext.register_base_class()

#: This variable contains the link name for the case shortcut
#: association proxy
RELATED_CASES_LINK_NAME = "_related_cases"


def get_edge_src(edge: psqlgraph.Edge) -> Optional[psqlgraph.Node]:
    """Look up edge source node by id if the association proxy is not set.

    Args:
        edge: edge whose source node we are looking for

    Returns:
        Return the edge's source or None.
    """
    node_cls = edge.get_node_class()

    if edge.src:
        src = edge.src
    elif edge.src_id is not None:
        src_class = node_cls.get_subclass_named(edge.__src_class__)
        src = edge.get_session().query(src_class).filter(src_class.node_id == edge.src_id).first()
    else:
        src = None
    return src


def get_edge_dst(edge: psqlgraph.Edge, allow_query: bool = False) -> Optional[psqlgraph.Node]:
    """Look up edge destination node.

    Args:
        edge: edge whose destination node we are looking for
        allow_query: whether we can query db by node id

    Returns:
        Return the edge's destination or None.
    """
    node_cls = edge.get_node_class()

    if edge.dst:
        dst = edge.dst
    elif edge.dst_id is not None and allow_query:

        dst_class = node_cls.get_subclass_named(edge.__dst_class__)
        dst = edge.get_session().query(dst_class).filter(dst_class.node_id == edge.dst_id).first()
    else:
        dst = None

    return dst


def get_related_cases_from_cache(node: psqlgraph.Node) -> List[psqlgraph.Node]:
    """Get the cached related case ids from this node's case shortcut edges.

    Args:
        node: The Node instance

    Returns:
        List of Case nodes
    """
    return [case for case in getattr(node, RELATED_CASES_LINK_NAME, []) if case is not None]


def get_related_case_edge_cls_name(node: psqlgraph.Node) -> str:
    """Generate shortcut edge class name.

    Args:
        node: The source node of the edge

    Returns:
        the related case edge class name
    """
    return f"{node.__class__.__name__}RelatesToCase"


def get_related_cases_from_parents(node: psqlgraph.Node) -> List[psqlgraph.Node]:
    """Get the cached related case ids from the parents of this node.

    Get the cached related case ids from the parents of this node from
    1. The shortcut edges of any parent nodes
    2. If any parents are cases, include those ids

    Args:
        node: The Node instance

    Returns:
        List of Case nodes

    TODO: DEV-1261 DEV-1262
    """
    skip_edges_named = [get_related_case_edge_cls_name(node)]

    # Make sure the edges haven't been expunged
    edges_out = [e for e in node.edges_out if e in node.get_session()]

    # Get the cached ids from parents
    edges_out_filtered = (e for e in edges_out if e.__class__.__name__ not in skip_edges_named)
    dsts = (e.dst for e in edges_out_filtered if e.dst)
    cases_list: List[psqlgraph.Node] = sum(
        (dst._related_cases_from_cache for dst in dsts), start=[]
    )
    cases = set(cases_list)

    # Are any parents cases?
    for edge in edges_out:
        if edge.__class__.__name__ in skip_edges_named:
            continue
        node_cls = edge.get_node_class()
        dst_class = node_cls.get_subclass_named(edge.__dst_class__)
        if dst_class.label == "case" and edge.dst:
            cases.add(edge.dst)

    return [case for case in cases if case is not None]


class SecondaryKeyComparator(hybrid.Comparator):
    def __eq__(self, other: Iterable[Iterable[Any]]) -> bool:  # type: ignore
        """Compare 2 nodes and check whether they are the same.

            Given an Iterable of secondary keys and a node
            When checking whether the secondary keys are equal
            Then create dictionaries containing secondary keys and values from other
            And return True if the nodes have same values for those keys

        Args:
            other:
                _secondary_keys for the other node
        Returns:
            Ture iff the value for uniqueKeys are the same.
        """
        filters = []
        cls = self.__clause_element__()
        secondary_keys = getattr(cls, f"_{cls.__name__}__pg_secondary_keys", ())
        key_pairs = (
            (keys, values) for keys, values in zip(secondary_keys, other) if "id" not in keys
        )
        for keys, values in key_pairs:
            other_dict = {key: val for key, val in zip(keys, values)}
            filters.append(cls._props.contains(other_dict))
        return sqlalchemy.and_(*filters)
