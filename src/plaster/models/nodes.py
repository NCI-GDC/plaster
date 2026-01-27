import logging
from collections import OrderedDict
from collections.abc import Iterable
from typing import Any, Literal, NamedTuple, Optional, Union

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

DICTIONARY_KEYS: list[DICTIONARY_KEY_LITERAL] = [
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
    "null": ["type(None)"],
    "number": ["float", "int"],
}
EXCLUDED_PROPS = ["id", "type"]


logger = logging.getLogger(__name__)


class PropertyTypeMeta(NamedTuple):
    schema: dict[str, Any]

    @property
    def enums(self) -> Optional[list[str]]:
        return self.schema.get("enum")

    @property
    def type(self) -> list[str]:
        if "enum" in self.schema and "type" not in self.schema:
            return TYPE_MAPPING["string"]

        json_schema_type = self.schema["type"]
        _type = json_schema_type[0] if isinstance(json_schema_type, list) else json_schema_type
        return TYPE_MAPPING[_type]


class PropertyMeta(NamedTuple):
    name: str
    schema: dict[str, Any]

    def type_metas(self) -> list[PropertyTypeMeta]:
        ty = []
        if "oneOf" in self.schema:
            ty = [PropertyTypeMeta(e) for e in self.schema["oneOf"]]
        if "type" in self.schema or "enum" in self.schema:
            ty = [PropertyTypeMeta(self.schema)]
        return ty

    @property
    def types(self) -> tuple[list[str], list[str]]:
        f_types: set[str] = set()
        f_enums: set[str] = set()
        for meta in self.type_metas():
            f_types |= set(meta.type)
            if meta.enums:
                f_enums |= set(meta.enums)
        return sorted(f_types), sorted(f_enums)


class LinkMetadata(NamedTuple):
    edges_out: str
    dst_type: str
    backref: str


class BackRefMetadata(NamedTuple):
    name: str
    src_type: str


class EdgeMetadata(NamedTuple):
    backref: str
    type: str


class NodeMetadata(NamedTuple):
    label: str
    associations: set[str]
    schema: psqlgml.DictionarySchemaDict
    backrefs_dict: dict[str, dict[str, BackRefMetadata]]
    dictionary_version: str
    plaster_version: str

    @property
    def class_name(self) -> str:
        return "".join([a.capitalize() for a in self.label.split("_")])

    @property
    def table_name(self) -> str:
        return f"node_{self.label.replace('_', '')}"

    @property
    def defaults(self) -> dict[str, Union[bool, float, int, str]]:
        return {
            key: values["default"]
            for key, values in self.schema["properties"].items()
            if "default" in values
        }

    @property
    def dictionary(self) -> dict[str, Any]:
        return {key: self.schema[key] for key in DICTIONARY_KEYS if key in self.schema}

    @property
    def properties(self) -> Iterable[PropertyMeta]:
        logger.info(f"Reading schema for node: {self.class_name}")
        for key, schema in self.schema["properties"].items():
            if key in EXCLUDED_PROPS or key in self.associations:
                continue
            yield PropertyMeta(key, schema)

    @property
    def backrefs_metadata(self) -> dict[str, BackRefMetadata]:
        """Generate data for _pg_backrefs -- in_edges(links from other types).

        _pg_backrefs is not required for Nodes and Edges to work correctly. it's
        used by some repo to get in_edges types.

        Returns:
            dictionary of 'in' edges
        """
        return OrderedDict(sorted(self.backrefs_dict[self.label].items()))

    @property
    def edges_metadata(self) -> dict[str, EdgeMetadata]:
        """Generate data for _pg_edges -- all edges(links to and from other types).

        _pg_edges is not required for Nodes and Edges to work correctly. It's used by
        some repo to get all edges types.

        Returns:
            dictionary of all edges
        """
        edges_metadata: dict[str, EdgeMetadata] = {}
        for name, link in self.links_metadata.items():
            edges_metadata[name] = EdgeMetadata(link.backref, link.dst_type)

        for name, back_ref in self.backrefs_metadata.items():
            edges_metadata[name] = EdgeMetadata(back_ref.name, back_ref.src_type)
        return OrderedDict(sorted(edges_metadata.items()))

    @property
    def links_metadata(self) -> dict[str, LinkMetadata]:
        """Generate data for _pg_links -- out_edges(links to other types).

        _pg_links is not required for Nodes and Edges to work correctly, It's used by
        some repo to get out edges types.

        Returns:
            dictionary of out edges
        """
        links_metadata: dict[str, LinkMetadata] = {}
        for name, link in utils.get_links(self.schema).items():
            edge_name = utils.parse_edge(self.schema, link)
            links_metadata[name] = LinkMetadata(
                edge_name, link["target_type"], link["backref"]
            )
        return OrderedDict(sorted(links_metadata.items()))

    @property
    def tag_props(self) -> Optional[list[str]]:
        """Keys specified in the dictionary, used for generation of tags.

        Returns:
            list of keys used to generate tags
        """
        return self.schema.get("tagProperties")

    @property
    def tag_config(self) -> dict[str, Any]:
        return self.schema.get("tagBuilderConfig", {})  # type: ignore

    @property
    def secondary_keys(self) -> list[list[str]]:
        unique_keys = self.schema.get("uniqueKeys", [])
        return [keys for keys in unique_keys if "id" not in keys]
