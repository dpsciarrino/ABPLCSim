# engine/type_registry.py
#
# Responsibilities:
#   - Define the TagType enum for all supported primitive and structured types
#   - Define FieldDefinition (a single named+typed field within a UDT)
#   - Define TypeDefinition (a named UDT composed of FieldDefinitions)
#   - Implement TypeRegistry, which:
#       * Pre-loads all built-in types (BOOL, SINT, INT, DINT, REAL, TIMER, COUNTER)
#       * Accepts registration of user-defined UDTs
#       * Validates that all field types exist before accepting a UDT
#       * Detects and rejects circular UDT references
#       * Rejects duplicate type name registration
#
# Dependencies: none (this module has no imports from within this project)
#
# TODO: Implement TagType, FieldDefinition, TypeDefinition, TypeRegistry

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging
logger = logging.getLogger(__name__)

# Integer range constants — used by Tag for type enforcement
SINT_MIN, SINT_MAX   = -128, 127
INT_MIN,  INT_MAX    = -32_768, 32_767
DINT_MIN, DINT_MAX   = -2_147_483_648, 2_147_483_647

class TagType(Enum):
    BOOL = "BOOL"
    SINT = "SINT"
    INT = "INT"
    DINT = "DINT"
    REAL = "REAL"
    TIMER = "TIMER"
    COUNTER = "COUNTER"

@dataclass
class FieldDefinition:
    name:      str
    type_name: str  # e.g. "BOOL", "DINT", "TIMER", or a custom UDT name

@dataclass
class TypeDefinition:
    name:   str
    fields: list[FieldDefinition] = field(default_factory=list)

    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Return the FieldDefinition for a given field name, or None."""
        for f in self.fields:
            if f.name == field_name:
                return f
        return None

class TypeRegistry:
    # Names of built-in types that cannot be overwritten by user UDTs
    BUILTIN_NAMES: set[str] = {t.value for t in TagType}

    def __init__(self) -> None:
        # Internal store: type_name (str) -> TypeDefinition
        self._types: dict[str, TypeDefinition] = {}
        self._load_builtins()
    
    def _load_builtins(self) -> None:
        """Pre-load all built-in type definitions. Called once at init."""

        # Primitives - no fields, just a named type entry
        for primitive in ["BOOL", "SINT", "INT", "DINT", "REAL"]:
            self._types[primitive] = TypeDefinition(name=primitive)
        
        # TIMER - built-in structured 
        self._types["TIMER"] = TypeDefinition(
            name="TIMER",
            fields=[
                FieldDefinition("PRE", "DINT"),
                FieldDefinition("ACC", "DINT"),
                FieldDefinition("EN",  "BOOL"),
                FieldDefinition("TT",  "BOOL"),
                FieldDefinition("DN",  "BOOL"),
            ]
        )

        # COUNTER — built-in structured type
        self._types["COUNTER"] = TypeDefinition(
            name="COUNTER",
            fields=[
                FieldDefinition("PRE", "DINT"),
                FieldDefinition("ACC", "DINT"),
                FieldDefinition("CU",  "BOOL"),
                FieldDefinition("CD",  "BOOL"),
                FieldDefinition("DN",  "BOOL"),
                FieldDefinition("OV",  "BOOL"),
                FieldDefinition("UN",  "BOOL"),
            ]
        )

    def register(self, type_def: TypeDefinition) -> None:
        """
        Register a user-defined type.

        Raises:
            ValueError: if the name is a built-in type name
            ValueError: if the name is already registered
            ValueError: if any field references an unknown type
            ValueError: if registering this type would create a circular reference
        """
        if type_def.name in self.BUILTIN_NAMES:
            raise ValueError(
                f"Cannot register '{type_def.name}': name is reserved for a built-in type."
            )

        if type_def.name in self._types:
            raise ValueError(
                f"Type '{type_def.name}' is already registered."
            )

        # Validate all field types exist before accepting the definition
        for f in type_def.fields:
            if f.type_name not in self._types:
                raise ValueError(
                    f"Field '{f.name}' in type '{type_def.name}' references "
                    f"unknown type '{f.type_name}'."
                )

        # Check for circular references before committing
        self._check_circular(type_def.name, type_def, visited=set())

        self._types[type_def.name] = type_def

    def get(self, type_name: str) -> TypeDefinition:
        """
        Return the TypeDefinition for a given type name.

        Raises:
            KeyError: if the type name is not registered
        """
        if type_name not in self._types:
            raise KeyError(f"Unknown type: '{type_name}'.")
        return self._types[type_name]

    def exists(self, type_name: str) -> bool:
        """Return True if the type name is registered."""
        return type_name in self._types
    
    def _check_circular(
        self,
        root_name: str,
        type_def: TypeDefinition,
        visited: set[str]
    ) -> None:
        """
        Recursively check that type_def does not reference root_name
        anywhere in its field hierarchy.

        Raises:
            ValueError: if a circular reference is detected
        """
        for f in type_def.fields:
            if f.type_name == root_name:
                raise ValueError(
                    f"Circular reference detected: type '{root_name}' "
                    f"cannot contain a field of its own type."
                )
            # Only recurse into registered structured types, not primitives
            if f.type_name in self._types and f.type_name not in visited:
                visited.add(f.type_name)
                self._check_circular(
                    root_name,
                    self._types[f.type_name],
                    visited
                )