# tests/test_type_registry.py
#
# Test specification for engine.type_registry
# All tests are written before implementation (TDD).
# Each test currently raises NotImplementedError or ImportError until implemented.
#
# Run with: pytest tests/test_type_registry.py -v

import pytest
from engine.type_registry import (
    TagType, FieldDefinition, TypeDefinition, TypeRegistry
)

# ── TagType enum ──────────────────────────────────────────────────────────────

class TestTagType:
    def test_primitive_types_exist(self):
        """BOOL, SINT, INT, DINT, REAL must all be defined."""
        for name in ["BOOL", "SINT", "INT", "DINT", "REAL"]:
            assert TagType(name).value == name

    def test_structured_types_exist(self):
        """TIMER and COUNTER must be defined."""
        for name in ["TIMER", "COUNTER"]:
            assert TagType(name).value == name


# ── TypeRegistry — built-in types ────────────────────────────────────────────

@pytest.fixture
def registry():
    """Returns a fresh TypeRegistry for each test."""
    return TypeRegistry()

class TestTypeRegistryBuiltins():
    def test_bool_is_preloaded(self, registry):
        assert registry.exists("BOOL")

    def test_sint_is_preloaded(self, registry):
        assert registry.exists("SINT")

    def test_int_is_preloaded(self, registry):
        assert registry.exists("INT")

    def test_dint_is_preloaded(self, registry):
        assert registry.exists("DINT")

    def test_real_is_preloaded(self, registry):
        assert registry.exists("REAL")

    def test_timer_is_preloaded(self, registry):
        assert registry.exists("TIMER")

    def test_counter_is_preloaded(self, registry):
        assert registry.exists("COUNTER")

    def test_builtin_type_cannot_be_overwritten(self, registry):
        """Registering a UDT named BOOL or TIMER must raise an error."""
        with pytest.raises(ValueError, match="reserved"):
            registry.register(TypeDefinition(name="BOOL"))


# ── TypeRegistry — UDT registration ──────────────────────────────────────────

class TestTypeRegistryUDT:
    def test_register_valid_udt(self, registry):
        """A UDT with all known field types is accepted."""
        motor = TypeDefinition(
            name="MotorControl",
            fields=[
                FieldDefinition("Running",  "BOOL"),
                FieldDefinition("Speed",    "DINT"),
            ]
        )
        registry.register(motor)
        assert registry.exists("MotorControl")

    def test_register_udt_with_unknown_field_type_raises(self, registry):
        """A field referencing a type that hasn't been registered must raise."""
        bad = TypeDefinition(
            name="BadType",
            fields=[FieldDefinition("X", "NonExistentType")]
        )
        with pytest.raises(ValueError, match="unknown type"):
            registry.register(bad)

    def test_register_duplicate_type_name_raises(self, registry):
        """Registering two UDTs with the same name must raise."""
        t = TypeDefinition(name="MyType", fields=[])
        registry.register(t)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(TypeDefinition(name="MyType", fields=[]))

    def test_register_udt_with_nested_udt_field(self, registry):
        """A UDT field that references another registered UDT is accepted."""
        inner = TypeDefinition(name="Inner", fields=[FieldDefinition("X", "BOOL")])
        outer = TypeDefinition(name="Outer", fields=[FieldDefinition("Inner", "Inner")])
        registry.register(inner)
        registry.register(outer)
        assert registry.exists("Outer")

    def test_register_udt_with_timer_field(self, registry):
        """A UDT field of type TIMER (built-in structured) is accepted."""
        t = TypeDefinition(
            name="WithTimer",
            fields=[FieldDefinition("RunTimer", "TIMER")]
        )
        registry.register(t)
        assert registry.exists("WithTimer")


# ── TypeRegistry — circular reference detection ───────────────────────────────

class TestTypeRegistryCircularRef:
    def test_direct_circular_reference_raises(self, registry):
        """UDT 'A' with a field of type 'A' must raise."""
        # A has a field of type A — illegal
        # Must register A first to make "A" a known type, then attempt re-register
        registry._types["A"] = TypeDefinition(
            name="A",
            fields=[FieldDefinition("self_ref", "A")]
        )
        circular = TypeDefinition(
            name="B",
            fields=[FieldDefinition("a_field", "A")]
        )
        with pytest.raises(ValueError, match="[Cc]ircular"):
            registry._check_circular("A", registry._types["A"], set())

    def test_indirect_circular_reference_raises(self, registry):
        """UDT 'A' → field of type 'B' → field of type 'A' must raise."""
        # Register A → B, then try to register B → A
        registry._types["A"] = TypeDefinition(
            name="A", fields=[FieldDefinition("b", "B")]
        )
        b_def = TypeDefinition(
            name="B", fields=[FieldDefinition("a", "A")]
        )
        with pytest.raises(ValueError, match="[Cc]ircular"):
            registry._check_circular("A", b_def, set())

    def test_non_circular_chain_is_accepted(self, registry):
        """UDT 'A' → field of type 'B' → field of primitive is accepted."""
        inner = TypeDefinition(name="Inner", fields=[FieldDefinition("x", "DINT")])
        outer = TypeDefinition(name="Outer", fields=[FieldDefinition("i", "Inner")])
        registry.register(inner)
        registry.register(outer)  # should not raise
        assert registry.exists("Outer")
