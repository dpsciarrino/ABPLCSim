# engine/path_resolver.py
#
# Responsibilities:
#   - Define PathToken base and subtypes: NameToken, IndexToken
#   - Implement tokenize(path: str) → list[PathToken]
#       * Splits a path string like "motors[2].RunTimer.ACC" into tokens
#       * NameToken("motors"), IndexToken(2), NameToken("RunTimer"), NameToken("ACC")
#   - Implement resolve_get(tag, tokens) → value
#       * Traverses a Tag's value structure following the token list
#       * Raises errors for: out-of-bounds index, unknown member, index on non-array,
#         member access on non-struct
#   - Implement resolve_set(tag, tokens, value, type_registry) → None
#       * Traverses to the target location and validates type before writing
#       * Raises errors for type mismatches and invalid paths
#
# Note: Single-dimension arrays only for MVP.
#       Multi-dimensional array support is deferred — see docs/known_limitations.md
#
# Dependencies: engine.tag, engine.type_registry
#
# TODO: Implement PathToken, NameToken, IndexToken, tokenize, resolve_get, resolve_set

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re
import logging

from engine.type_registry import TypeRegistry
from engine.tag import (
    Tag, TimerValue, CounterValue,
    StructInstance, ArrayInstance, validate_value
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class NameToken:
    name: str

    def __repr__(self) -> str:
        return f"NameToken({self.name!r})"


@dataclass(frozen=True)
class IndexToken:
    index: int

    def __repr__(self) -> str:
        return f"IndexToken({self.index})"


PathToken = NameToken | IndexToken

# Regex patterns used by the tokenizer
_NAME_RE  = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)')
_INDEX_RE = re.compile(r'^\[(\d+)\]')
_DOT_RE   = re.compile(r'^\.') 


class PathResolver:

    def __init__(self, registry: TypeRegistry) -> None:
        self._registry = registry

    def split_root(self, path: str) -> tuple[str, str]:
        """
        Split a full tag path into (root_name, sub_path).

        Examples:
            "valve_open"           → ("valve_open", "")
            "MyTimer.ACC"          → ("MyTimer", "ACC")
            "motors[2].Running"    → ("motors", "[2].Running")

        Raises:
            ValueError: if path is empty or does not start with a valid identifier
        """
        if not path:
            raise ValueError("Tag path cannot be empty.")

        match = _NAME_RE.match(path)
        if not match:
            raise ValueError(
                f"Invalid path '{path}': must start with a valid identifier."
            )

        root_name = match.group(1)
        remainder = path[match.end():]

        # Strip leading dot separator if present
        if remainder.startswith("."):
            remainder = remainder[1:]
            if not remainder:
                raise ValueError(
                    f"Invalid path '{path}': trailing dot with no member name."
                )

        return root_name, remainder

    def tokenize(self, sub_path: str) -> list[PathToken]:
        """
        Tokenize a sub_path (everything after the root tag name) into
        a list of NameTokens and IndexTokens.

        Empty sub_path returns an empty list — meaning access the tag directly.

        Examples:
            ""                  → []
            "ACC"               → [NameToken("ACC")]
            "[2].Running"       → [IndexToken(2), NameToken("Running")]
            "[2].RunTimer.ACC"  → [IndexToken(2), NameToken("RunTimer"), NameToken("ACC")]

        Raises:
            ValueError: if the path contains invalid syntax
        """
        if not sub_path:
            return []

        tokens: list[PathToken] = []
        remaining = sub_path

        while remaining:
            # Try index token first: [n]
            index_match = _INDEX_RE.match(remaining)
            if index_match:
                tokens.append(IndexToken(int(index_match.group(1))))
                remaining = remaining[index_match.end():]
                # After an index, optional dot then member name
                dot_match = _DOT_RE.match(remaining)
                if dot_match:
                    remaining = remaining[dot_match.end():]
                    if not remaining:
                        raise ValueError(
                            f"Invalid sub_path '{sub_path}': "
                            f"trailing dot after index."
                        )
                continue

            # Try name token: identifier
            name_match = _NAME_RE.match(remaining)
            if name_match:
                tokens.append(NameToken(name_match.group(1)))
                remaining = remaining[name_match.end():]
                # After a name, optional dot then next token
                dot_match = _DOT_RE.match(remaining)
                if dot_match:
                    remaining = remaining[dot_match.end():]
                    if not remaining:
                        raise ValueError(
                            f"Invalid sub_path '{sub_path}': "
                            f"trailing dot after member name."
                        )
                continue

            # Nothing matched — invalid syntax
            raise ValueError(
                f"Invalid sub_path '{sub_path}': "
                f"unexpected characters at '{remaining}'."
            )

        logger.debug(f"Tokenized '{sub_path}' → {tokens}")
        return tokens

    def _get_struct_type_name(self, value: Any) -> str:
        """
        Return the registry type name for a structured value.
        Handles TimerValue, CounterValue, and StructInstance.

        Raises:
            TypeError: if value is not a known structured type
        """
        if isinstance(value, TimerValue):
            return "TIMER"
        if isinstance(value, CounterValue):
            return "COUNTER"
        if isinstance(value, StructInstance):
            return value.type_name
        raise TypeError(
            f"Expected a structured value, got {type(value).__name__!r}."
        )

    def resolve_get(self, tag: Tag, sub_path: str) -> Any:
        """
        Traverse tag's value structure and return the value at sub_path.

        Empty sub_path returns the tag's top-level value directly.

        Raises:
            KeyError:   unknown member name
            IndexError: array index out of bounds
            TypeError:  invalid traversal (e.g. indexing a primitive)
        """
        tokens = self.tokenize(sub_path)

        if not tokens:
            return tag.get_value()

        current = tag.get_value()

        for token in tokens:
            if isinstance(token, IndexToken):
                if not isinstance(current, ArrayInstance):
                    raise TypeError(
                        f"Cannot apply index [{token.index}] to "
                        f"non-array value of type {type(current).__name__!r}."
                    )
                current = current.get_element(token.index)

            elif isinstance(token, NameToken):
                if isinstance(current, (TimerValue, CounterValue, StructInstance)):
                    type_name = self._get_struct_type_name(current)
                    type_def  = self._registry.get(type_name)
                    field_def = type_def.get_field(token.name)
                    if field_def is None:
                        raise KeyError(
                            f"'{token.name}' is not a member of {type_name}."
                        )
                    if isinstance(current, StructInstance):
                        current = current.get_field(token.name)
                    else:
                        current = getattr(current, token.name)
                else:
                    raise TypeError(
                        f"Cannot access member '{token.name}' on "
                        f"primitive value of type {type(current).__name__!r}."
                    )

        logger.debug(f"resolve_get '{tag.name}/{sub_path}' → {current!r}")
        return current
    
    def resolve_set(self, tag: Tag, sub_path: str, value: Any) -> None:
        """
        Traverse tag's value structure and write value at sub_path.

        Empty sub_path writes directly to a primitive tag's top-level value.
        Writing to a struct or array leaf (non-primitive destination) raises.

        Raises:
            TypeError:  wrong Python type for the destination field
            ValueError: value out of range for the destination field
            KeyError:   unknown member name
            IndexError: array index out of bounds
        """
        tokens = self.tokenize(sub_path)

        # Empty path — direct primitive write
        if not tokens:
            tag.set_value(value)
            return

        current = tag.get_value()

        # Traverse all tokens except the last
        for token in tokens[:-1]:
            if isinstance(token, IndexToken):
                if not isinstance(current, ArrayInstance):
                    raise TypeError(
                        f"Cannot apply index [{token.index}] to "
                        f"non-array value of type {type(current).__name__!r}."
                    )
                current = current.get_element(token.index)

            elif isinstance(token, NameToken):
                if isinstance(current, (TimerValue, CounterValue, StructInstance)):
                    type_name = self._get_struct_type_name(current)
                    type_def  = self._registry.get(type_name)
                    field_def = type_def.get_field(token.name)
                    if field_def is None:
                        raise KeyError(
                            f"'{token.name}' is not a member of {type_name}."
                        )
                    if isinstance(current, StructInstance):
                        current = current.get_field(token.name)
                    else:
                        current = getattr(current, token.name)
                else:
                    raise TypeError(
                        f"Cannot access member '{token.name}' on "
                        f"primitive value of type {type(current).__name__!r}."
                    )

        # Handle the final token — the write destination
        final_token = tokens[-1]

        if isinstance(final_token, IndexToken):
            if not isinstance(current, ArrayInstance):
                raise TypeError(
                    f"Cannot apply index [{final_token.index}] to "
                    f"non-array value of type {type(current).__name__!r}."
                )
            validate_value(current.element_type_name, value)
            current.set_element(final_token.index, value)

        elif isinstance(final_token, NameToken):
            if not isinstance(current, (TimerValue, CounterValue, StructInstance)):
                raise TypeError(
                    f"Cannot access member '{final_token.name}' on "
                    f"primitive value of type {type(current).__name__!r}."
                )
            type_name = self._get_struct_type_name(current)
            type_def  = self._registry.get(type_name)
            field_def = type_def.get_field(final_token.name)
            if field_def is None:
                raise KeyError(
                    f"'{final_token.name}' is not a member of {type_name}."
                )
            # Enforce destination must be a primitive leaf
            dest_type_def = self._registry.get(field_def.type_name)
            if dest_type_def.fields:
                raise TypeError(
                    f"Cannot write directly to structured member "
                    f"'{final_token.name}' of type '{field_def.type_name}'. "
                    f"Write to individual primitive members instead."
                )
            validate_value(field_def.type_name, value)
            if isinstance(current, StructInstance):
                current.set_field(final_token.name, value)
            else:
                setattr(current, final_token.name, value)

        logger.debug(
            f"resolve_set '{tag.name}/{sub_path}' ← {value!r}"
        )
    
    