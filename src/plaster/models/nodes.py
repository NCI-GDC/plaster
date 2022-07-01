import logging
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
)

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


class LinkMetadata(NamedTuple):
    edges_out: str
    dst_type: str


class BackRefMetadata(NamedTuple):
    name: str
    src_type: str


class EdgeMetadata(NamedTuple):
    backref: str
    type: str


@attr.s(auto_attribs=True)
class NodeMetadata:
    label: str
    associations: Set[str]
    schema: psqlgml.DictionarySchemaDict
    backrefs_dict: Dict[str, Dict[str, BackRefMetadata]]

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
    def pg_backrefs(self) -> Dict[str, BackRefMetadata]:
        """Generate data for _pg_backrefs -- in_edges(links from other types).

        _pg_backrefs is not required for Nodes and Edges to work correctly. it's
        used by some repo to get in_edges types.

        Returns:
            dictionary of in edges
        """
        return self.backrefs_dict[self.label]

    @property
    def pg_edges(self) -> Dict[str, EdgeMetadata]:
        """Generate data for _pg_edges -- all edges(links to and from other types).

        _pg_edges is not required for Nodes and Edges to work correctly. It's used by
        some repo to get all edges types.

        Returns:
            dictionary of all edges
        """
        pg_edges: Dict[str, EdgeMetadata] = {}
        for name, link in self.pg_links.items():
            pg_edges[name] = EdgeMetadata(self._find_backref(link, self.label), link.dst_type)

        for name, back_ref in self.pg_backrefs.items():
            pg_edges[name] = EdgeMetadata(back_ref.name, back_ref.src_type)
        return pg_edges

    @property
    def pg_links(self) -> Dict[str, LinkMetadata]:
        """Generate data for _pg_links -- out_edges(links to other types).

        _pg_links is not required for Nodes and Edges to work correctly, It's used by
        some repo to get out edges types.

        Returns:
            dictionary of out edges
        """
        pg_links: Dict[str, LinkMetadata] = {}
        for name, link in utils.get_links(self.schema).items():
            edge_name = utils.parse_edge(self.schema, link)
            pg_links[link["name"]] = LinkMetadata(edge_name, link["target_type"])
        return pg_links

    def _find_backref(self, link: LinkMetadata, label: str) -> str:
        for name, backref in self.backrefs_dict[link.dst_type].items():
            if backref.src_type == label:
                return name
        return ""
