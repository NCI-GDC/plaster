import logging
from typing import Any, Dict, Iterable, List, Literal, Optional, Set, Tuple, Union

import attr
import psqlgml

from plaster import utils

DICTIONARY_KEY_LITERAL = Literal[
    "title",
    "namespace",
    "category",
    "submittable",
    "downloadable",
    "description",
    "required",
    "project",
    "program",
    "previous_version_downloadable",
]

DICTIONARY_KEYS: List[DICTIONARY_KEY_LITERAL] = [
    "title",
    "namespace",
    "category",
    "submittable",
    "downloadable",
    "description",
    "required",
    "project",
    "program",
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
EXCLUDED_PROPS = ["id", "type"]


logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class PropertyTypeMeta:
    schema: Dict[str, Any]

    @property
    def enums(self) -> Optional[List[str]]:
        return self.schema.get("enum")

    @property
    def type(self) -> List[str]:

        if "enum" in self.schema and "type" not in self.schema:
            return TYPE_MAPPING["string"]

        json_schema_type = self.schema["type"]
        _type = json_schema_type[0] if isinstance(json_schema_type, list) else json_schema_type
        return TYPE_MAPPING[_type]


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
    def types(self) -> Tuple[List[str], List[str]]:
        f_types: List[str] = []
        f_enums: List[str] = []
        for meta in self.type_metas():
            f_types += meta.type
            if meta.enums:
                f_enums = meta.enums
        return f_types, f_enums


@attr.s(auto_attribs=True)
class NodeMeta:
    label: str
    associations: Set[str]
    schema: psqlgml.DictionarySchemaDict
    backref_dict: Dict[str, Dict[str, Dict[str, str]]]

    @property
    def back_refs(self) -> Dict[str, Dict[str, str]]:
        return self.backref_dict[self.label]

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
    def dictionary(self) -> Dict[str, Any]:
        return {key: self.schema[key] for key in DICTIONARY_KEYS if key in self.schema}

    @property
    def properties(self) -> Iterable[PropertyMeta]:
        logger.info(f"Reading schema for node: {self.class_name}")
        for key, schema in self.schema["properties"].items():
            if key in EXCLUDED_PROPS or key in self.associations:
                continue
            yield PropertyMeta(key, schema)

    @property
    def pg_links(self) -> Dict[str, Dict[str, str]]:
        pg_links = {}
        for name, link in utils.get_links(self.schema).items():
            edge_name = utils.parse_edge(self.schema, link)
            pg_links[link["name"]] = {"edge_out": edge_name, "dst_type": link["target_type"]}
        return pg_links
