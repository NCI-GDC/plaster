import psqlgml


def get_links(schema: psqlgml.types.DictionarySchemaDict) -> dict[str, psqlgml.types.Link]:
    """Given a schema, pull out all the ``links`` that this type can have an edge to.

    :returns: a ``dict`` of format ``{<name>: <link>}``

    """
    links = {}
    for entry in schema["links"]:
        if "subgroup" in entry:
            for link in entry["subgroup"]:
                links[link["name"]] = link
        else:
            links[entry["name"]] = entry
    return links


def get_class_name_from_id(_id: str) -> str:
    return "".join([a.capitalize() for a in _id.split("_")])


def parse_edge(
    subschema: psqlgml.types.DictionarySchemaDict,
    link: psqlgml.types.Link,
) -> str:
    """Parse an edge from the dictionary and create and Edge subclass.

    :returns: The outbound name of the edge

    """
    dst_label = link["target_type"]
    edge_label = link["label"]
    src_label = subschema["id"]
    edge_name = "".join(map(get_class_name_from_id, (src_label, edge_label, dst_label)))

    return f"_{edge_name}_out"
