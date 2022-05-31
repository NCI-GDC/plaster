import hashlib
import logging
from typing import Optional

import attr
import psqlgml

from plaster.models.nodes import NodeMeta

logger = logging.getLogger(__name__)


def generate_table_name(src_label: str, label: str, dst_label: str) -> str:
    """Generate a name for the edge table.

    Because of the limit on table name length on PostgreSQL, we have
    to truncate some of the longer names.  To do this we concatenate
    the first 2 characters of each word in each of the input arguments
    up to 10 characters (per argument).  However, this strategy would
    very likely lead to collisions in naming.  Therefore, we take the
    first 8 characters of a hash of the full, un-truncated name
    *before* we truncate and prepend this to the truncation.  This
    gets us a name like ``edge_721d393f_LaLeSeqDaFrLaLeSeBu``.  This
    is rather an undesirable workaround. - jsm
    """
    table_name = (
        f"edge_{src_label.replace('_', '')}{label.replace('_', '')}{dst_label.replace('_', '')}"
    )

    # If the name is too long, prepend it with the first 8 hex of it's hash
    # truncate the each part of the name
    if len(table_name) <= 40:
        return table_name

    logger.debug(f"Edge table_name {table_name} too long, shortening")
    shortened_name = hashlib.md5(table_name.encode()).hexdigest()[:8]
    shortened_label = "".join([a[:2] for a in label.split("_")])[:7]
    shortened_dst_label = "".join([a[:2] for a in dst_label.split("_")])[:10]
    shortened_src_label = "".join([a[:2] for a in src_label.split("_")])[:10]

    shortened_table_name = (
        f"edge_{shortened_name}_{shortened_src_label}{shortened_label}{shortened_dst_label}"
    )
    logger.debug("Shortening {} -> {}".format(table_name, shortened_table_name))

    return shortened_table_name


def sentence_case(item: str) -> str:
    return "".join([a.capitalize() for a in item.split("_")])


@attr.s(auto_attribs=True)
class EdgeMeta:
    association: psqlgml.Association
    src: NodeMeta
    dst: NodeMeta

    @property
    def class_name(self) -> str:

        src = sentence_case(self.association.src)
        label = sentence_case(self.association.label)
        dst = sentence_case(self.association.dst)
        return f"{src}{label}{dst}"

    @property
    def dst_class(self) -> str:
        return self.dst.class_name

    @property
    def dst_src_assoc(self) -> Optional[str]:
        return self.association.backref

    @property
    def dst_table(self) -> str:
        return self.dst.table_name

    @property
    def label(self) -> str:
        return self.association.label

    @property
    def src_class(self) -> str:
        return self.src.class_name

    @property
    def src_dst_assoc(self) -> str:
        return self.association.name

    @property
    def src_table(self) -> str:
        return self.dst.table_name

    @property
    def table_name(self) -> str:
        return generate_table_name(
            self.association.src, self.association.label, self.association.dst
        )
