import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, NamedTuple, Set

import black
import jinja2 as j
import psqlgml
from psqlgml import types

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


def get_links(schema: types.DictionarySchema) -> List[Dict[str, Dict[str, str]]]:
    """Given a schema, pull out all of the ``links`` that this type can have an edge to.

    :returns: a ``dict`` of format ``{<name>: <link>}``

    """
    links = {}
    for entry in schema.links:
        if "subgroup" in entry:
            for link in entry["subgroup"]:
                links[link["name"]] = link
        else:
            links[entry["name"]] = entry
    return links


def process_dictionary_for_backrefs(
    dic: psqlgml.Dictionary,
) -> Dict[str, Dict[str, Dict[str, str]]]:
    backref_dict = defaultdict(dict)
    for label, schema in dic.schema.items():
        for link in get_links(schema).values():
            backref_dict[link["target_type"]][link["backref"]] = {
                "name": link["name"],
                "src_type": label,
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
