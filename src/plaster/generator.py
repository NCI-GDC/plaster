import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple, Set

import black
import jinja2 as j
import psqlgml

from plaster.models import edges, nodes
from plaster.types import PgBackRef

env = j.Environment(  # nosec B701
    loader=j.PackageLoader("plaster"),
    autoescape=j.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)
OUTPUT_LOCATION = "examples/models"

logger = logging.getLogger(__name__)


class ImportMeta(NamedTuple):
    package: str
    class_name: str


def generate_edges(
    associations: Set[psqlgml.Association],
    node_metas: Dict[str, nodes.NodeMetaData],
) -> Iterable[edges.EdgeMetaData]:
    """Read dictionary associations and generate metadata for edges.

    Args:
        associations: associations between nodes
        node_metas: node metadata

    Returns:
        A generator of node metadata
    """
    for assoc in associations:
        if assoc.is_reference:
            continue

        src = node_metas[assoc.src]
        dst = node_metas[assoc.dst]
        meta = edges.EdgeMetaData(assoc, src, dst)
        logger.info(f"Reading edge: {meta.class_name}")

        yield meta


def process_dictionary_for_backrefs(
    dic: psqlgml.Dictionary,
) -> Dict[str, Dict[str, PgBackRef]]:
    """Preprocess dictionary links to populate node class _pg_backrefs later.

    Args:
        dic: gdcdictionary or biodictioanry

    Returns:
        A dict containing node name and node backrefs.
    """
    backrefs_dict: Dict[str, Dict[str, PgBackRef]] = defaultdict(dict)

    for assoc in dic.all_associations():
        if assoc.backref is None:
            continue
        backrefs_dict[assoc.dst][assoc.backref] = PgBackRef(assoc.name, assoc.src)
    return backrefs_dict


def generate_nodes(dic: psqlgml.Dictionary) -> Dict[str, nodes.NodeMetaData]:
    """Read dictionary and generate metadata for nodes.

    Args:
        dic: dictionary to read, gdcdictionary or biodictionary

    Returns:
        metadata for nodes
    """
    backrefs_dict = process_dictionary_for_backrefs(dic)

    node_metas: Dict[str, nodes.NodeMetaData] = {}

    for label, schema in dic.schema.items():
        associations = {a.name for a in dic.associations(label)}
        meta = nodes.NodeMetaData(label, associations, schema.raw, backrefs_dict)
        node_metas[label] = meta
    return node_metas


def generate(dictionary: psqlgml.Dictionary, output_dir: str = OUTPUT_LOCATION) -> None:
    """Generate the edges and nodes classes from dictionary.

    Args:
        dictionary: gdcdictionary or biodictionary to read
        output_dir: directory to save the classes

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    import_metas: Set["ImportMeta"] = set()

    node_metas = generate_nodes(dictionary)
    for meta in node_metas.values():
        render_and_write_file(meta, "node", output_dir, meta.label)
        import_metas.add(ImportMeta(package=meta.label, class_name=meta.class_name))

    edges_meta_generator = generate_edges(dictionary.all_associations(), node_metas)

    for edge_meta in edges_meta_generator:
        render_and_write_file(edge_meta, "edge", output_dir, edge_meta.class_name.lower())
        import_metas.add(
            ImportMeta(package=edge_meta.class_name.lower(), class_name=edge_meta.class_name)
        )

    render_and_write_file(import_metas, "init", output_dir, "__init__")


def render_and_write_file(
    meta: Any, template_base_name: str, output_dir: str, file_base_name: str
) -> None:
    """Write node, edge, etc to python file.

    Args:
        meta: metadata for jinja template
        template_base_name: base name for jinja template to use
        output_dir: output directory
        file_base_name: base name for python file

    Returns:
        None
    """
    template = env.get_template(f"{template_base_name}.jinja2")
    rendered = template.render(meta=meta)
    rendered = black.format_str(rendered, mode=black.FileMode())
    loc = Path(f"{output_dir}/{file_base_name}.py")
    with loc.open("w") as f:
        f.write(rendered)
