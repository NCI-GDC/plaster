import hashlib
import logging
from typing import Tuple, Type

import psqlgraph
from sqlalchemy import Index, func

logger = logging.getLogger(__name__)


def index_name(cls: Type[psqlgraph.Node], description: str) -> str:
    """Standardize index naming.

        Because of PostgreSQL's name character
        limit, this follows a similar scheme to shortening edge names in
        `gdcdatamodel.generate_edge_tablename()`
        For long names, take the first 8 characters of a hash of the full,
        un-truncated table name *before* we truncate and prepend this to
        the truncation.  This gets us a name like
        ``index_4df72441_famihist_lower_submitte_id``.  This is yet
        another rather an undesirable workaround. - jsm

    Args:
        cls: node class to build index with
        description: usually the field name to index

    Returns:
        index name
    """
    name = "index_{}_{}".format(cls.__tablename__, description)

    # If the name is too long, prepend it with the first 8 hex of it's hash
    # truncate the each part of the name
    if len(name) > 40:
        old_name = name
        logger.debug(f"index name '{old_name}' too long, shortening")
        name = "index_{}_{}_{}".format(
            hashlib.md5(cls.__tablename__.encode("utf-8")).hexdigest()[:8],
            "".join([a[:4] for a in cls.get_label().split("_")])[:20],
            "_".join([a[:8] for a in description.split("_")])[:25],
        )

        logger.debug("Shortening {} -> {}".format(old_name, name))

    return name


def get_secondary_key_indexes(cls: Type[psqlgraph.Node]) -> Tuple:
    """Get tuple of indexes on the secondary keys of the class.

    Args:
        cls: Class to create indexes

    Returns:
        Tuple of indexes
    """
    #: use text_pattern_ops, allows LIKE statements not starting with %
    index_op = "text_pattern_ops"
    secondary_keys = {
        key for keys in getattr(cls, f"_{cls.__name__}__pg_secondary_keys", []) for key in keys
    }

    key_indexes = (
        Index(
            index_name(cls, key),
            cls._props[key].astext.label(key),
            postgresql_ops={key: index_op},
        )
        for key in secondary_keys
    )

    lower_key_indexes = (
        Index(
            index_name(cls, key + "_lower"),
            func.lower(cls._props[key].astext).label(key + "_lower"),
            postgresql_ops={key + "_lower": index_op},
        )
        for key in secondary_keys
    )

    return tuple(key_indexes) + tuple(lower_key_indexes)
