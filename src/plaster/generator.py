import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, NamedTuple, Set

import black
import jinja2 as j
import psqlgml

from plaster.models import edges, nodes

env = j.Environment(  # nosec B701
    loader=j.PackageLoader("plaster"),
    autoescape=j.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)
OUTPUT_LOCATION = "examples/models"
import_metas: Set["ImportMeta"] = set()
logger = logging.getLogger(__name__)


class ImportMeta(NamedTuple):
    package: str
    class_name: str


def generate_edges(
    associations: Set[psqlgml.Association],
    node_metas: Dict[str, nodes.NodeMeta],
    output_location: str,
) -> None:

    template = env.get_template("edge.jinja2")
    for assoc in associations:
        if assoc.is_reference:
            continue

        src = node_metas[assoc.src]
        dst = node_metas[assoc.dst]
        meta = edges.EdgeMeta(assoc, src, dst)
        logger.info(f"Reading edge: {meta.class_name}")
        rendered = template.render(meta=meta)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{output_location}/{meta.class_name.lower()}.py")

        import_metas.add(ImportMeta(package=meta.class_name.lower(), class_name=meta.class_name))
        with loc.open("w") as f:
            f.write(rendered)


def process_dictionary_for_backrefs(
    dic: psqlgml.Dictionary,
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Preprocess dictionary links to populate node class _pg_backrefs later.

    Args:
        dic: gdcdictionary or biodictioanry

    Returns:
        A dict containing node name and node backrefs.
    """
    backref_dict: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(dict)

    for assoc in dic.all_associations():
        if assoc.backref is None:
            continue
        backref_dict[assoc.dst][assoc.backref] = {
            "name": assoc.name,
            "src_type": assoc.src,
        }
    return backref_dict


def generate_nodes(
    dic: psqlgml.Dictionary, output_dir: str = OUTPUT_LOCATION
) -> Dict[str, nodes.NodeMeta]:
    template = env.get_template("node.jinja2")

    backref_dict = process_dictionary_for_backrefs(dic)

    node_metas: Dict[str, nodes.NodeMeta] = {}
    os.makedirs(output_dir, exist_ok=True)

    for label, schema in dic.schema.items():

        associations = {a.name for a in dic.associations(label)}

        meta = nodes.NodeMeta(label, associations, schema.raw, backref_dict[label])
        rendered = template.render(meta=meta)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{output_dir}/{label}.py")

        import_metas.add(ImportMeta(package=meta.label, class_name=meta.class_name))
        with loc.open("w") as f:
            f.write(rendered)
        node_metas[label] = meta
    return node_metas


def generate(dictionary: psqlgml.Dictionary, output_dir: str = OUTPUT_LOCATION) -> None:
    node_metas = generate_nodes(dictionary, output_dir)
    generate_edges(dictionary.all_associations(), node_metas, output_dir)

    template = env.get_template("init.jinja2")
    rendered = template.render(imports=import_metas)
    rendered = black.format_str(rendered, mode=black.FileMode())
    loc = Path(f"{output_dir}/__init__.py")
    with loc.open("w") as f:
        f.write(rendered)
