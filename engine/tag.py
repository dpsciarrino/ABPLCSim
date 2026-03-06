# engine/tag.py
#
# Responsibilities:
#   - Define TimerValue dataclass (PRE, ACC, EN, TT, DN)
#   - Define CounterValue dataclass (PRE, ACC, CU, CD, DN, OV, UN)
#   - Define StructInstance — holds field_name → value for a UDT instance
#   - Define ArrayInstance — holds a fixed-size list of typed elements
#   - Define Tag — the unit stored in TagDB:
#       * name: str
#       * type_name: str  (references a type in the TypeRegistry)
#       * value: any      (TimerValue | CounterValue | StructInstance |
#                          ArrayInstance | bool | int | float)
#   - Tag is created externally and registered with TagDB (Option B pattern)
#   - Default value initialization is handled here, not in TagDB
#
# Dependencies: engine.type_registry
#
# TODO: Implement TimerValue, CounterValue, StructInstance, ArrayInstance, Tag

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import logging

from engine.type_registry import (
    TypeRegistry, TypeDefinition, FieldDefinition, TagType,
    SINT_MIN, SINT_MAX,
    INT_MIN,  INT_MAX,
    DINT_MIN, DINT_MAX,
)

logger = logging.getLogger(__name__)

@dataclass
class TimerValue:
    PRE: int  = 0
    ACC: int  = 0
    EN:  bool = False
    TT:  bool = False
    DN:  bool = False


@dataclass
class CounterValue:
    PRE: int  = 0
    ACC: int  = 0
    CU:  bool = False
    CD:  bool = False
    DN:  bool = False
    OV:  bool = False
    UN:  bool = False

@dataclass
class StructInstance:
    type_name: str
    fields:    dict[str, Any] = field(default_factory=dict)

    def get_field(self, name: str) -> Any:
        if name not in self.fields:
            raise KeyError(
                f"Field '{name}' does not exist on struct '{self.type_name}'."
            )
        return self.fields[name]

    def set_field(self, name: str, value: Any) -> None:
        if name not in self.fields:
            raise KeyError(
                f"Field '{name}' does not exist on struct '{self.type_name}'."
            )
        self.fields[name] = value

@dataclass
class ArrayInstance:
    element_type_name: str
    elements:          list[Any] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.elements)

    def get_element(self, index: int) -> Any:
        if index < 0 or index >= len(self.elements):
            raise IndexError(
                f"Index {index} out of bounds for array of size {len(self.elements)}."
            )
        return self.elements[index]

    def set_element(self, index: int, value: Any) -> None:
        if index < 0 or index >= len(self.elements):
            raise IndexError(
                f"Index {index} out of bounds for array of size {len(self.elements)}."
            )
        self.elements[index] = value


def validate_value(type_name: str, value: Any) -> None:
    """
    Validate that value is legal for the given primitive type_name.
    Only validates primitive types — structured types (TIMER, COUNTER, UDTs)
    and arrays are validated field-by-field at write time via PathResolver.

    Raises:
        TypeError:  if the value is the wrong Python type entirely
        ValueError: if the value is the right type but out of range
    """

    if type_name == "BOOL":
        # Accept True, False, 0, 1 only
        # Must check bool before int because bool is a subclass of int in Python
        if isinstance(value, bool):
            if value not in (True, False):
                raise ValueError(f"BOOL value must be True or False, got {value!r}.")
            return
        if isinstance(value, int):
            if value not in (0, 1):
                raise ValueError(f"BOOL accepts 0 or 1 only, got {value!r}.")
            return
        raise TypeError(f"BOOL requires bool or int (0/1), got {type(value).__name__!r}.")

    if type_name == "SINT":
        if isinstance(value, bool):
            raise TypeError("SINT does not accept bool values.")
        if not isinstance(value, int):
            raise TypeError(f"SINT requires int, got {type(value).__name__!r}.")
        if not (SINT_MIN <= value <= SINT_MAX):
            raise ValueError(f"SINT value {value} out of range ({SINT_MIN} to {SINT_MAX}).")
        return

    if type_name == "INT":
        if isinstance(value, bool):
            raise TypeError("INT does not accept bool values.")
        if not isinstance(value, int):
            raise TypeError(f"INT requires int, got {type(value).__name__!r}.")
        if not (INT_MIN <= value <= INT_MAX):
            raise ValueError(f"INT value {value} out of range ({INT_MIN} to {INT_MAX}).")
        return

    if type_name == "DINT":
        if isinstance(value, bool):
            raise TypeError("DINT does not accept bool values.")
        if not isinstance(value, int):
            raise TypeError(f"DINT requires int, got {type(value).__name__!r}.")
        if not (DINT_MIN <= value <= DINT_MAX):
            raise ValueError(f"DINT value {value} out of range ({DINT_MIN} to {DINT_MAX}).")
        return

    if type_name == "REAL":
        if isinstance(value, bool):
            raise TypeError("REAL does not accept bool values.")
        # Accept both float and int (e.g. writing 0 to a REAL tag is valid)
        if not isinstance(value, (int, float)):
            raise TypeError(f"REAL requires float or int, got {type(value).__name__!r}.")
        return

    # Structured types and UDTs are not validated here —
    # their members are validated individually at write time
    logger.debug(f"validate_value: '{type_name}' is a structured type, skipping primitive check.")

def _default_value(type_name: str, registry: TypeRegistry) -> Any:
    """
    Produce the correct default value for a given type name.
    Recursively initializes UDT fields and array elements.
    """
    if type_name == "BOOL":
        return False
    if type_name in ("SINT", "INT", "DINT"):
        return 0
    if type_name == "REAL":
        return 0.0
    if type_name == "TIMER":
        return TimerValue()
    if type_name == "COUNTER":
        return CounterValue()

    # Must be a UDT or array — look it up in the registry
    type_def = registry.get(type_name)

    # UDT — recursively initialize each field
    instance = StructInstance(type_name=type_name)
    for f in type_def.fields:
        instance.fields[f.name] = _default_value(f.type_name, registry)
    logger.debug(f"Initialized StructInstance for type '{type_name}'.")
    return instance

class Tag:
    """
    A named, typed value — the fundamental unit stored in TagDB.

    Created externally and registered with TagDB (Option B pattern).
    The registry is used at init time for default value generation
    and type lookups, but not stored permanently.
    """

    def __init__(
        self,
        name:        str,
        type_name:   str,
        registry:    TypeRegistry,
        array_size:  Optional[int] = None,
    ) -> None:
        if not name:
            raise ValueError("Tag name cannot be empty.")
        if not registry.exists(type_name):
            raise ValueError(f"Unknown type '{type_name}' — register it before creating tags.")

        self.name      = name
        self.type_name = type_name
        self._array_size = array_size

        # Initialize default value
        if array_size is not None:
            if array_size < 1:
                raise ValueError(f"Array size must be at least 1, got {array_size}.")
            self.value: Any = ArrayInstance(
                element_type_name=type_name,
                elements=[_default_value(type_name, registry) for _ in range(array_size)]
            )
            logger.debug(f"Tag '{name}' created as ARRAY[{array_size}] OF {type_name}.")
        else:
            self.value = _default_value(type_name, registry)
            logger.debug(f"Tag '{name}' created as {type_name}.")

    @property
    def is_array(self) -> bool:
        return isinstance(self.value, ArrayInstance)

    @property
    def is_struct(self) -> bool:
        return isinstance(self.value, (StructInstance, TimerValue, CounterValue))

    @property
    def is_primitive(self) -> bool:
        return not self.is_array and not self.is_struct

    def set_value(self, new_value: Any) -> None:
        """
        Set the top-level value of this tag.
        Only valid for primitive tags — struct and array members
        are written via PathResolver.

        Raises:
            TypeError:  wrong Python type for this tag's type
            ValueError: value out of range for this tag's type
        """
        if not self.is_primitive:
            raise TypeError(
                f"Tag '{self.name}' is a {self.type_name} — "
                f"use PathResolver to write to individual members."
            )
        validate_value(self.type_name, new_value)
        self.value = new_value
        logger.debug(f"Tag '{self.name}' set to {new_value!r}.")

    def get_value(self) -> Any:
        return self.value

    def __repr__(self) -> str:
        return f"Tag(name={self.name!r}, type={self.type_name!r}, value={self.value!r})"