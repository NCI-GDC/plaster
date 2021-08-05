import logging
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Dict,
    Final,
    FrozenSet,
    List,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
    cast,
)

import yaml
from jsonschema import RefResolver

logger = logging.getLogger(__name__)

DEFAULT_META_SCHEMA: Final[str] = "metaschema.yaml"
DEFAULT_DEFINITIONS: FrozenSet[str] = frozenset(
    [
        "_definitions.yaml",
        "_terms.yaml",
        "_terms_enum.yaml",
    ]
)

T = TypeVar("T")
Category = Literal[
    "administrative",
    "analysis",
    "biospecimen",
    "clinical",
    "data",
    "data_bundle",
    "data_file",
    "index_file",
    "metadata_file",
    "notation",
    "qc_bundle",
    "TBD",
]
RESOLVERS: Dict[str, "Resolver"] = {}


class Link(TypedDict):
    exclusive: bool
    required: bool
    name: str
    label: str
    target_type: str
    backref: str
    multiplicity: str


class SubGroupedLink(Link, total=False):
    subgroup: List[Link]


class SchemaDict(TypedDict):
    id: str
    title: str
    namespace: str
    category: Category
    submittable: bool
    downloadable: bool
    previous_version_downloadable: bool
    description: str
    links: List[SubGroupedLink]
    properties: Dict[str, Any]
    required: List[str]
    systemProperties: List[str]
    tagProperties: List[str]
    uniqueKeys: List[List[str]]


@dataclass()
class Schema:
    raw: SchemaDict

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def title(self) -> str:
        return self.raw["title"]

    @property
    def namespace(self) -> str:
        return self.raw["namespace"]

    @property
    def category(self) -> Category:
        return self.raw["category"]

    @property
    def submittable(self) -> bool:
        return self.raw["submittable"]

    @property
    def downloadable(self) -> bool:
        return self.raw["downloadable"]

    @property
    def previous_version_downloadable(self) -> bool:
        return self.raw["previous_version_downloadable"]

    @property
    def description(self) -> str:
        return self.raw["description"]

    @property
    def system_properties(self) -> List[str]:
        return self.raw["systemProperties"]

    @property
    def links(self) -> List[SubGroupedLink]:
        return self.raw["links"]

    @property
    def required(self) -> List[str]:
        return self.raw["required"]

    @property
    def unique_keys(self) -> List[List[str]]:
        return self.raw["uniqueKeys"]

    @property
    def properties(self) -> Dict[str, Any]:
        return self.raw["properties"]


@dataclass()
class Resolver:
    name: str
    schema: Dict[str, Any]

    @property
    def local(self) -> RefResolver:
        return RefResolver("#", self.schema)

    @property
    def ref(self) -> RefResolver:
        return RefResolver(f"{self.name}#", self.schema)

    def resolve(self, reference: str) -> Any:
        base, _ = reference.split("#", 1)
        resolver = RESOLVERS[base] if base else self
        ref = resolver.ref
        _, resolution = ref.resolve(reference)
        return resolve_schema(resolution, resolver)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.name}>"


@dataclass(frozen=True)
class Dictionary:
    schema: Dict[str, Schema]


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schemas(directory: str, meta_schema: str, definitions: FrozenSet[str]) -> Dictionary:

    excludes: FrozenSet[str] = frozenset([meta_schema] + list(definitions))
    raw_schemas: List[SchemaDict] = []

    definitions_paths = Path(directory)
    for definition in definitions_paths.iterdir():
        if definition.is_dir() or definition.name == "README.md":
            continue

        path = definition.name
        schema = load_yaml(definition)
        RESOLVERS[path] = Resolver(name=path, schema=schema)
        if path not in excludes:
            raw_schemas.append(cast(SchemaDict, schema))

    return _load_schema(raw_schemas)


def resolve_schema(entry: T, resolver: Optional[Resolver] = None) -> T:

    # unit entries
    if not isinstance(entry, (list, dict)):
        return entry

    # handle list
    if isinstance(entry, list):
        return cast(T, [resolve_schema(e, resolver) for e in entry])

    resolved: Dict[str, Any] = {}
    for k, v in entry.items():
        if k == "$ref":
            refs = v
            if not isinstance(refs, list):
                refs = [v]

            for ref in refs:
                resolution = resolve_ref(ref, resolver)
                resolved.update(resolution)
        else:
            resolved[k] = resolve_schema(v, resolver)
    return cast(T, resolved)


def resolve_ref(reference: str, resolver: Optional[Resolver] = None) -> Any:
    logger.debug(f"Resolving reference: {reference} with resolver: {resolver}")

    base, _ = reference.split("#", 1)
    if not resolver or (base and resolver.name != base):
        resolver = RESOLVERS[base]
    return resolver.resolve(reference)


def _load_schema(schemas: List[SchemaDict]) -> Dictionary:
    loaded: Dict[str, Schema] = {}
    for schema in schemas:
        logger.debug(f"Resolving dictionary schema with id: {schema['id']}")

        raw: SchemaDict = resolve_schema(schema)
        loaded[schema["id"]] = Schema(raw=raw)

        logger.debug(f"Schema resolution complete for schema id: {schema['id']}")
    return Dictionary(schema=loaded)


def load(
    schema_dir: str,
    meta_schema: str = DEFAULT_META_SCHEMA,
    definitions: Optional[FrozenSet[str]] = None,
) -> Dictionary:
    logger.info(f"loading dictionary from {schema_dir}")
    definitions = definitions or DEFAULT_DEFINITIONS
    return load_schemas(schema_dir, meta_schema, definitions)
