import itertools
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple, Optional, Set

import black
import jinja2 as j
import psqlgml

from plaster.models import edges, nodes

NOT_RELATED_CASES_CATEGORIES = {
    "administrative",
    "TBD",
}

RELATED_CASE_LINK_NAME = "_related_cases"

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
    node_metas: Dict[str, nodes.NodeMetadata],
) -> Iterable[edges.EdgeMetadata]:
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
        meta = edges.EdgeMetadata(assoc, src, dst)
        logger.info(f"Reading edge: {meta.class_name}")

        yield meta


def generate_relates_to_case_edges(
    node_metas: Dict[str, nodes.NodeMetadata]
) -> Iterable[edges.EdgeMetadata]:
    """Generate relates to case edge metadata.

        Given metadata for all the nodes
        When this function is called
        Then it will find The case node and all other nodes has relates_to case edges
        And yield edge_meta for those edges

    Args:
        node_metas: the metadata for all the node classes to generate

    Returns::
        A generator of edge metadata for relates_to case edges
    """
    case_meta = node_metas["case"]
    for label, node_meta in node_metas.items():
        if label == "annotation":
            continue
        if node_meta.dictionary["category"] in NOT_RELATED_CASES_CATEGORIES:
            continue

        association = psqlgml.Association(
            src=label,
            dst="case",
            label="relates_to",
            name=RELATED_CASE_LINK_NAME,
            backref=f"_related_{label}",
            is_reference=False,
        )
        edge_meta = edges.EdgeMetadata(association, node_meta, case_meta)
        logger.debug(f"Creating {label} relates to case({case_meta}): {edge_meta}")
        yield edge_meta


def process_dictionary_for_backrefs(
    dic: psqlgml.Dictionary,
) -> Dict[str, Dict[str, nodes.BackRefMetadata]]:
    """Preprocess dictionary links to populate node class _pg_backrefs later.

    Args:
        dic: gdcdictionary or biodictioanry

    Returns:
        A dict containing node name and node backrefs.
    """
    backrefs_dict: Dict[str, Dict[str, nodes.BackRefMetadata]] = defaultdict(dict)

    for assoc in dic.all_associations():
        if assoc.backref is None:
            continue
        backrefs_dict[assoc.dst][assoc.backref] = nodes.BackRefMetadata(assoc.name, assoc.src)
    return backrefs_dict


def generate_nodes(dic: psqlgml.Dictionary) -> Dict[str, nodes.NodeMetadata]:
    """Read dictionary and generate metadata for nodes.

    Args:
        dic: dictionary to read, gdcdictionary or biodictionary

    Returns:
        metadata for nodes
    """
    backrefs_dict = process_dictionary_for_backrefs(dic)

    node_metas: Dict[str, nodes.NodeMetadata] = {}

    for label, schema in dic.schema.items():
        associations = {a.name for a in dic.associations(label)}
        meta = nodes.NodeMetadata(label, associations, schema.raw, backrefs_dict)
        node_metas[label] = meta
    return node_metas


def generate(
    dictionary: psqlgml.Dictionary,
    output_dir: str = OUTPUT_LOCATION,
    namespace: Optional[str] = None,
) -> None:
    """Generate the edges and nodes classes from dictionary.

    Args:
        dictionary: gdcdictionary or biodictionary to read
        output_dir: directory to save the classes
        namespace: namespace for graph, useful when multiple graph are used at same time

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
    relates_to_case_edge_meta_generator = generate_relates_to_case_edges(node_metas)

    for edge_meta in itertools.chain(edges_meta_generator, relates_to_case_edge_meta_generator):
        render_and_write_file(edge_meta, "edge", output_dir, edge_meta.class_name.lower())
        import_metas.add(
            ImportMeta(package=edge_meta.class_name.lower(), class_name=edge_meta.class_name)
        )

    render_and_write_file(import_metas, "init", output_dir, "__init__")
    render_and_write_file(namespace, "base", output_dir, "base")
    render_and_write_file(None, "utils", output_dir, "utils")
    render_and_write_file(None, "versioning", output_dir, "versioning")


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
    rendered = render_template(meta, template_base_name)
    write_data_to_python_file(rendered, file_base_name, output_dir)


def write_data_to_python_file(data: str, file_base_name: str, output_dir: str) -> None:
    """Write data to python file.

    Args:
        data: content to write
        file_base_name: base name for the python file
        output_dir: directory to create the files

    Returns:
        None
    """
    loc = Path(f"{output_dir}/{file_base_name}.py")
    with loc.open("w") as f:
        f.write(data)


def render_template(meta: Any, template_base_name: str) -> str:
    """Render template with metadata to create concrete classes.

    Args:
        meta: node or edge metadata (or init metadata) for jinja template
        template_base_name: base name for jinja template file

    Returns:
        rendered content
    """
    try:
        template = env.get_template(f"{template_base_name}.jinja2")
    except j.exceptions.TemplateNotFound:
        template = env.get_template(f"{template_base_name}.py")
    rendered = template.render(meta=meta)
    rendered = black.format_str(rendered, mode=black.FileMode())
    return rendered
