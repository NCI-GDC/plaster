import functools
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

import attr
import black
import jinja2 as j
from psqlgml import dictionary, types

env = j.Environment(
    loader=j.PackageLoader("plaster"),
    autoescape=j.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

OUTPUT_LOCATION = "build"
DICTIONARY_KEYS = [
    "title",
    "namespace",
    "category",
    "submittable",
    "downloadable",
    "description",
    "required",
    "project",
    "program",
    "validators",
    "previous_version_downloadable",
]
TYPE_MAPPING = {
    "array": ["list"],
    "boolean": ["bool"],
    "float": ["float"],
    "integer": ["int"],
    "string": ["str"],
    "null": ["None"],
    "number": ["float", "int"],
}


@attr.s(auto_attribs=True)
class PropertyTypeMeta:
    schema: Dict[str, Any]

    @property
    def enums(self) -> Optional[List[str]]:
        return self.schema.get("enum")

    @property
    def type(self) -> List[Type]:

        if "enum" in self.schema and "type" not in self.schema:
            return TYPE_MAPPING.get("string")

        json_schema_type = self.schema["type"]
        return TYPE_MAPPING.get(json_schema_type)


@attr.s(auto_attribs=True)
class PropertyMeta:
    name: str
    schema: Dict[str, Any]

    def type_metas(self) -> List[PropertyTypeMeta]:
        ty = []
        if "oneOf" in self.schema:
            ty = [PropertyTypeMeta(e) for e in self.schema["oneOf"]]
        if "type" in self.schema or "enum" in self.schema:
            ty = [PropertyTypeMeta(self.schema)]
        return ty

    @property
    def types(self) -> Tuple[str, Optional[List[str]]]:
        f_types: List[Type] = []
        f_enums: Optional[List[str]] = None
        for meta in self.type_metas():
            f_types += meta.type
            if meta.enums:
                f_enums = meta.enums
        return f_types, f_enums


@attr.s(auto_attribs=True)
class ModelMeta:
    label: str
    schema: types.DictionarySchemaDict

    @property
    def class_name(self) -> str:
        return "".join([a.capitalize() for a in self.label.split("_")])

    @property
    def table_name(self) -> str:
        return "node_{}".format(self.label.replace("_", ""))

    @property
    def defaults(self) -> Dict[str, Union[bool, float, int, str]]:
        return {
            key: values["default"]
            for key, values in self.schema["properties"].items()
            if "default" in values
        }

    @property
    def dictionary(self):
        return {key: self.schema[key] for key in DICTIONARY_KEYS if key in self.schema}

    @property
    def properties(self) -> Iterable[PropertyMeta]:
        for key, schema in self.schema["properties"].items():
            yield PropertyMeta(key, schema)


def generate(dic: dictionary.Dictionary) -> None:
    template = env.get_template("model.jinja2")

    os.makedirs(OUTPUT_LOCATION)

    for label, schema in dic.schema.items():
        meta_data = ModelMeta(label, schema.raw)
        rendered = template.render(meta=meta_data)
        rendered = black.format_str(rendered, mode=black.FileMode())
        loc = Path(f"{OUTPUT_LOCATION}/{label}.py")

        with loc.open("w") as f:
            f.write(rendered)
