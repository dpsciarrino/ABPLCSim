# tests/test_type_registry.py
#
# Test specification for engine.type_registry
# All tests are written before implementation (TDD).
# Each test currently raises NotImplementedError or ImportError until implemented.
#
# Run with: pytest tests/test_type_registry.py -v

import pytest

# ── Imports (will fail until type_registry.py is implemented) ─────────────────
# from engine.type_registry import TagType, FieldDefinition, TypeDefinition, TypeRegistry


# ── TagType enum ──────────────────────────────────────────────────────────────

class TestTagType:
    def test_primitive_types_exist(self):
        """BOOL, SINT, INT, DINT, REAL must all be defined."""
        raise NotImplementedError

    def test_structured_types_exist(self):
        """TIMER and COUNTER must be defined."""
        raise NotImplementedError


# ── TypeRegistry — built-in types ────────────────────────────────────────────

class TestTypeRegistryBuiltins:
    def test_bool_is_preloaded(self):
        raise NotImplementedError

    def test_sint_is_preloaded(self):
        raise NotImplementedError

    def test_int_is_preloaded(self):
        raise NotImplementedError

    def test_dint_is_preloaded(self):
        raise NotImplementedError

    def test_real_is_preloaded(self):
        raise NotImplementedError

    def test_timer_is_preloaded(self):
        raise NotImplementedError

    def test_counter_is_preloaded(self):
        raise NotImplementedError

    def test_builtin_type_cannot_be_overwritten(self):
        """Registering a UDT named BOOL or TIMER must raise an error."""
        raise NotImplementedError


# ── TypeRegistry — UDT registration ──────────────────────────────────────────

class TestTypeRegistryUDT:
    def test_register_valid_udt(self):
        """A UDT with all known field types is accepted."""
        raise NotImplementedError

    def test_register_udt_with_unknown_field_type_raises(self):
        """A field referencing a type that hasn't been registered must raise."""
        raise NotImplementedError

    def test_register_duplicate_type_name_raises(self):
        """Registering two UDTs with the same name must raise."""
        raise NotImplementedError

    def test_register_udt_with_nested_udt_field(self):
        """A UDT field that references another registered UDT is accepted."""
        raise NotImplementedError

    def test_register_udt_with_timer_field(self):
        """A UDT field of type TIMER (built-in structured) is accepted."""
        raise NotImplementedError


# ── TypeRegistry — circular reference detection ───────────────────────────────

class TestTypeRegistryCircularRef:
    def test_direct_circular_reference_raises(self):
        """UDT 'A' with a field of type 'A' must raise."""
        raise NotImplementedError

    def test_indirect_circular_reference_raises(self):
        """UDT 'A' → field of type 'B' → field of type 'A' must raise."""
        raise NotImplementedError

    def test_non_circular_chain_is_accepted(self):
        """UDT 'A' → field of type 'B' → field of primitive is accepted."""
        raise NotImplementedError
