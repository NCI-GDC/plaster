import os
from pathlib import Path
from typing import Dict

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
OUTPUT_LOCATION = "build"


def generate(dic: psqlgml.Dictionary) -> None:
    template = env.get_template("model.jinja2")
    edge_template = env.get_template("edge.jinja2")

    node_metas: Dict[str, nodes.NodeMeta] = {}
    os.makedirs(OUTPUT_LOCATION, exist_ok=True)

    for label, schema in dic.schema.items():
        meta = nodes.NodeMeta(label, schema.raw)
        rendered = template.render(meta=meta)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{OUTPUT_LOCATION}/{label}.py")

        with loc.open("w") as f:
            f.write(rendered)
        node_metas[label] = meta

    edges.generate(dic.all_associations(), node_metas, edge_template, OUTPUT_LOCATION)
