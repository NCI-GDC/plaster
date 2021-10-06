import os
from pathlib import Path
from typing import Dict, List, NamedTuple, Set

import black
import jinja2 as j
import psqlgml

from plaster.models import edges, nodes

env = j.Environment(
    loader=j.PackageLoader("plaster"),
    autoescape=j.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)
OUTPUT_LOCATION = "examples/models"
import_metas: Set["ImportMeta"] = set()


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
        rendered = template.render(meta=meta)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{output_location}/{meta.class_name.lower()}.py")

        import_metas.add(ImportMeta(package=meta.class_name.lower(), class_name=meta.class_name))
        with loc.open("w") as f:
            f.write(rendered)


def generate_nodes(dic: psqlgml.Dictionary) -> Dict[str, nodes.NodeMeta]:
    template = env.get_template("node.jinja2")

    node_metas: Dict[str, nodes.NodeMeta] = {}
    os.makedirs(OUTPUT_LOCATION, exist_ok=True)

    for label, schema in dic.schema.items():

        associations = set([a.name for a in dic.associations(label)])

        meta = nodes.NodeMeta(label, associations, schema.raw)
        rendered = template.render(meta=meta)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{OUTPUT_LOCATION}/{label}.py")

        import_metas.add(ImportMeta(package=meta.label, class_name=meta.class_name))
        with loc.open("w") as f:
            f.write(rendered)
        node_metas[label] = meta
    return node_metas


def generate(dictionary: psqlgml.Dictionary) -> None:
    node_metas = generate_nodes(dictionary)
    generate_edges(dictionary.all_associations(), node_metas, OUTPUT_LOCATION)

    template = env.get_template("init.jinja2")
    rendered = template.render(imports=import_metas)
    rendered = black.format_str(rendered, mode=black.FileMode())
    loc = Path(f"{OUTPUT_LOCATION}/__init__.py")
    with loc.open("w") as f:
        f.write(rendered)
