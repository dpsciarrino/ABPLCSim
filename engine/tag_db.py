# engine/tag_db.py
#
# Responsibilities:
#   - Implement TagDB, which:
#       * Maintains an internal dict of tag_name → Tag
#       * register(tag: Tag) → None
#           - Accepts an externally created Tag and stores it
#           - Raises error if a tag with the same name already exists
#       * get(path: str) → value
#           - Delegates to PathResolver to traverse the path
#           - Raises error if the root tag name does not exist
#       * set(path: str, value) → None
#           - Delegates to PathResolver to traverse and write
#           - Type validation is enforced inside PathResolver
#       * exists(tag_name: str) → bool
#       * all_tags() → dict[str, Tag]
#           - Returns a snapshot of all registered tags (used by scan engine)
#
# Dependencies: engine.tag, engine.path_resolver, engine.type_registry
#
# TODO: Implement TagDB

from __future__ import annotations
from typing import Any
import logging

from engine.type_registry import TypeRegistry
from engine.tag import Tag
from engine.path_resolver import PathResolver

logger = logging.getLogger(__name__)


class TagDB:

    def __init__(self, registry: TypeRegistry) -> None:
        self._registry = registry
        self._resolver = PathResolver(registry)
        self._tags:     dict[str, Tag] = {}

    def register(self, tag: Tag) -> None:
        """
        Register a Tag instance in the database.

        Raises:
            ValueError: if a tag with the same name already exists
            ValueError: if the tag's type_name is not in the registry
        """
        if tag.name in self._tags:
            raise ValueError(
                f"Tag '{tag.name}' is already registered in this TagDB."
            )

        # Defensive re-check — Tag constructor already validates this,
        # but we verify here in case a Tag was constructed abnormally
        if not self._registry.exists(tag.type_name):
            raise ValueError(
                f"Tag '{tag.name}' has unregistered type '{tag.type_name}'. "
                f"Register the type in the TypeRegistry before registering the tag."
            )

        self._tags[tag.name] = tag
        logger.debug(f"Registered tag '{tag.name}' ({tag.type_name}).")

    def get(self, path: str) -> Any:
        """
        Return the value at the given path.

        Examples:
            get("valve_open")              → bool
            get("MyTimer.ACC")             → int
            get("motors[2].Running")       → bool
            get("motors[2].RunTimer.ACC")  → int

        Raises:
            KeyError:   root tag not found, or unknown member name
            IndexError: array index out of bounds
            TypeError:  invalid traversal (indexing a primitive, etc.)
        """
        root_name, sub_path = self._resolver.split_root(path)

        if root_name not in self._tags:
            raise KeyError(
                f"Tag '{root_name}' is not registered in this TagDB."
            )

        tag = self._tags[root_name]
        value = self._resolver.resolve_get(tag, sub_path)
        logger.debug(f"get('{path}') → {value!r}")
        return value

    def set(self, path: str, value: Any) -> None:
        """
        Write value to the given path.

        Raises:
            KeyError:   root tag not found, or unknown member name
            IndexError: array index out of bounds
            TypeError:  wrong Python type or invalid traversal
            ValueError: value out of range for destination type
        """
        root_name, sub_path = self._resolver.split_root(path)

        if root_name not in self._tags:
            raise KeyError(
                f"Tag '{root_name}' is not registered in this TagDB."
            )

        tag = self._tags[root_name]
        self._resolver.resolve_set(tag, sub_path, value)
        logger.debug(f"set('{path}', {value!r})")

    def exists(self, tag_name: str) -> bool:
        """Return True if a tag with this name is registered."""
        return tag_name in self._tags

    def get_tag(self, tag_name: str) -> Tag:
        """
        Return the Tag object itself (not its value).
        Used by the ScanCycleEngine to pass Tag objects to instructions.

        Raises:
            KeyError: if the tag is not registered
        """
        if tag_name not in self._tags:
            raise KeyError(
                f"Tag '{tag_name}' is not registered in this TagDB."
            )
        return self._tags[tag_name]

    def all_tags(self) -> dict[str, Tag]:
        """
        Return a snapshot copy of all registered tags.
        Modifying the returned dict does not affect the TagDB.
        """
        return dict(self._tags)

    def __repr__(self) -> str:
        return f"TagDB({list(self._tags.keys())})"