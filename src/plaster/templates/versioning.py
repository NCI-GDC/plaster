from typing import Any, Dict, Iterator, List

import psqlgraph


class TaggingConstraint:
    """Computes whether a node instance supports tagging or not."""

    def __init__(self, path: str, prop: str, values: List[str]) -> None:
        """Initialize TaggingConstraint.

        Args:
            path (str): full psqlgraph path to a parent node
            prop (str): valid node property name
            values (list[str]): list of possible value
        """
        self.path = path
        self.prop = prop
        self.values = values

    def _resolve_target_node_from_path(self, node: psqlgraph.Node) -> psqlgraph.Node:
        """Resolve to the final node instance that can be used to perform the matching.

        e.g: if path = `aligned_reads.submitted_alinged_reads`, the final node used to perform the matching
        is an instance of SubmittedAlignedReads, which can be reached by following the relationships defined in
        the path
            i.e: node["aligned_reads"][0]["submitted_aligned_reads"][0]
            this is equivalent to:
                node.aligned_reads[0].submitted_aligned_reads[0]

        Args:
            node (models.Node): Node instance

        Returns:
            models.Node: node instance whose properties will be used for matching
        """
        if not self.path:
            return node

        for path in self.path.split("."):
            # Since a node type can have multiple paths to a given parent
            # this check allows instances that do not have this specific path
            if len(node[path]) == 0:
                return None

            node = node[path][0]
        return node

    def match(self, node: psqlgraph.Node) -> bool:
        """Check if a node has a value matching the prop and values field.

        if it does, the particular instance will not participate in the entire tagging process

        Args:
            node (psqlgraph.Node): node instance

        Returns:
            Returns (bool)
        """
        node = self._resolve_target_node_from_path(node)
        return node and node[self.prop] in self.values


class TagBuilderConfig:
    """A wrapper around the tagBuilderConfig definition in the dictionary yaml."""

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

    def _constraints(self) -> Iterator[TaggingConstraint]:
        """Return all constraints defined for a particular node type."""
        skip_criterion = self.cfg.get("ignoreEntries", [])
        for criteria in skip_criterion:
            yield TaggingConstraint(
                path=criteria.get("path"),
                prop=criteria["prop"],
                values=criteria["values"],
            )

    def is_taggable(self, node: psqlgraph.Node) -> bool:
        """Return true if node supports tagging else False.

            Ideally, instances that return false will not
            have tag and version number set on them

        Returns:
            bool: True for nodes that can be tagged
        """
        return not any(criteria.match(node) for criteria in self._constraints())
