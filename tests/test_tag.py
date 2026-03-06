# tests/test_tag.py
#
# Test specification for engine.tag
# All tests are written before implementation (TDD).
#
# Run with: pytest tests/test_tag.py -v

import pytest
from engine.type_registry import TypeRegistry, TypeDefinition, FieldDefinition
from engine.tag import (
    Tag, TimerValue, CounterValue,
    StructInstance, ArrayInstance, validate_value
)

@pytest.fixture
def registry():
    return TypeRegistry()

@pytest.fixture
def registry_with_motor(registry):
    """Registry pre-loaded with a MotorControl UDT for struct tests."""
    registry.register(TypeDefinition(
        name="MotorControl",
        fields=[
            FieldDefinition("Running",  "BOOL"),
            FieldDefinition("Speed",    "DINT"),
            FieldDefinition("RunTimer", "TIMER"),
        ]
    ))
    return registry

# ── TimerValue defaults ───────────────────────────────────────────────────────

class TestTimerValue:
    def test_default_pre_is_zero(self):
        assert TimerValue().PRE == 0

    def test_default_acc_is_zero(self):
        assert TimerValue().ACC == 0

    def test_default_en_is_false(self):
        assert TimerValue().EN is False

    def test_default_tt_is_false(self):
        assert TimerValue().TT is False

    def test_default_dn_is_false(self):
        assert TimerValue().DN is False


# ── CounterValue defaults ─────────────────────────────────────────────────────

class TestCounterValue:
    def test_default_pre_is_zero(self):
        assert CounterValue().PRE == 0

    def test_default_acc_is_zero(self):
        assert CounterValue().ACC == 0

    def test_default_status_bits_are_false(self):
        c = CounterValue()
        assert c.CU is False
        assert c.CD is False
        assert c.DN is False
        assert c.OV is False
        assert c.UN is False


# ── Tag creation — primitives ─────────────────────────────────────────────────

class TestTagPrimitiveDefaults:
    def test_bool_tag_defaults_to_false(self, registry):
        assert Tag("x", "BOOL", registry).get_value() is False

    def test_sint_tag_defaults_to_zero(self, registry):
        assert Tag("x", "SINT", registry).get_value() == 0

    def test_int_tag_defaults_to_zero(self, registry):
        assert Tag("x", "INT", registry).get_value() == 0

    def test_dint_tag_defaults_to_zero(self, registry):
        assert Tag("x", "DINT", registry).get_value() == 0

    def test_real_tag_defaults_to_zero_float(self, registry):
        assert Tag("x", "REAL", registry).get_value() == 0.0

    def test_unknown_type_raises(self, registry):
        with pytest.raises(ValueError, match="Unknown type"):
            Tag("x", "NONEXISTENT", registry)

    def test_empty_name_raises(self, registry):
        with pytest.raises(ValueError, match="empty"):
            Tag("", "BOOL", registry)


# ── Tag creation — structured ─────────────────────────────────────────────────

class TestTagStructuredDefaults:
    def test_timer_tag_value_is_timer_value(self, registry):
        tag = Tag("t", "TIMER", registry)
        assert isinstance(tag.get_value(), TimerValue)

    def test_counter_tag_value_is_counter_value(self, registry):
        tag = Tag("c", "COUNTER", registry)
        assert isinstance(tag.get_value(), CounterValue)

    def test_udt_tag_value_is_struct_instance(self, registry_with_motor):
        tag = Tag("m", "MotorControl", registry_with_motor)
        assert isinstance(tag.get_value(), StructInstance)

    def test_udt_fields_recursively_initialized(self, registry_with_motor):
        tag = Tag("m", "MotorControl", registry_with_motor)
        s = tag.get_value()
        assert s.get_field("Running") is False
        assert s.get_field("Speed") == 0

    def test_udt_nested_timer_field_is_timer_value(self, registry_with_motor):
        tag = Tag("m", "MotorControl", registry_with_motor)
        s = tag.get_value()
        assert isinstance(s.get_field("RunTimer"), TimerValue)


# ── Tag creation — arrays ─────────────────────────────────────────────────────

class TestTagArrayDefaults:
    def test_array_of_bool(self, registry):
        tag = Tag("flags", "BOOL", registry, array_size=4)
        arr = tag.get_value()
        assert isinstance(arr, ArrayInstance)
        assert arr.size == 4
        assert all(v is False for v in arr.elements)

    def test_array_of_dint(self, registry):
        tag = Tag("counts", "DINT", registry, array_size=3)
        arr = tag.get_value()
        assert all(v == 0 for v in arr.elements)

    def test_array_of_udt(self, registry_with_motor):
        tag = Tag("motors", "MotorControl", registry_with_motor, array_size=2)
        arr = tag.get_value()
        assert arr.size == 2
        assert all(isinstance(e, StructInstance) for e in arr.elements)

    def test_array_size_zero_raises(self, registry):
        with pytest.raises(ValueError, match="at least 1"):
            Tag("x", "BOOL", registry, array_size=0)

    def test_is_array_true_for_array_tag(self, registry):
        tag = Tag("x", "BOOL", registry, array_size=2)
        assert tag.is_array is True

    def test_is_array_false_for_primitive_tag(self, registry):
        tag = Tag("x", "BOOL", registry)
        assert tag.is_array is False


# ── Tag type enforcement ──────────────────────────────────────────────────────

class TestValidateValue:
    def test_bool_accepts_true(self):
        validate_value("BOOL", True)

    def test_bool_accepts_false(self):
        validate_value("BOOL", False)

    def test_bool_accepts_zero(self):
        validate_value("BOOL", 0)

    def test_bool_accepts_one(self):
        validate_value("BOOL", 1)

    def test_bool_rejects_two(self):
        with pytest.raises(ValueError):
            validate_value("BOOL", 2)

    def test_bool_rejects_float(self):
        with pytest.raises(TypeError):
            validate_value("BOOL", 1.0)

    def test_bool_rejects_string(self):
        with pytest.raises(TypeError):
            validate_value("BOOL", "true")

    def test_sint_accepts_min(self):
        validate_value("SINT", -128)

    def test_sint_accepts_max(self):
        validate_value("SINT", 127)

    def test_sint_rejects_below_min(self):
        with pytest.raises(ValueError):
            validate_value("SINT", -129)

    def test_sint_rejects_above_max(self):
        with pytest.raises(ValueError):
            validate_value("SINT", 128)

    def test_sint_rejects_bool(self):
        with pytest.raises(TypeError):
            validate_value("SINT", True)

    def test_sint_rejects_float(self):
        with pytest.raises(TypeError):
            validate_value("SINT", 1.0)

    def test_int_accepts_bounds(self):
        validate_value("INT", -32_768)
        validate_value("INT", 32_767)

    def test_int_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            validate_value("INT", 32_768)

    def test_dint_accepts_bounds(self):
        validate_value("DINT", -2_147_483_648)
        validate_value("DINT", 2_147_483_647)

    def test_dint_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            validate_value("DINT", 2_147_483_648)

    def test_dint_rejects_bool(self):
        with pytest.raises(TypeError):
            validate_value("DINT", True)

    def test_real_accepts_float(self):
        validate_value("REAL", 3.14)

    def test_real_accepts_int(self):
        validate_value("REAL", 0)

    def test_real_rejects_string(self):
        with pytest.raises(TypeError):
            validate_value("REAL", "3.14")

    def test_real_rejects_bool(self):
        with pytest.raises(TypeError):
            validate_value("REAL", True)


# ── Tag.set_value ─────────────────────────────────────────────────────────────

class TestTagSetValue:
    def test_set_bool_tag(self, registry):
        tag = Tag("v", "BOOL", registry)
        tag.set_value(True)
        assert tag.get_value() is True

    def test_set_dint_tag(self, registry):
        tag = Tag("v", "DINT", registry)
        tag.set_value(42)
        assert tag.get_value() == 42

    def test_set_wrong_type_raises(self, registry):
        tag = Tag("v", "DINT", registry)
        with pytest.raises(TypeError):
            tag.set_value("hello")

    def test_set_out_of_range_raises(self, registry):
        tag = Tag("v", "SINT", registry)
        with pytest.raises(ValueError):
            tag.set_value(999)

    def test_set_value_on_struct_tag_raises(self, registry):
        tag = Tag("t", "TIMER", registry)
        with pytest.raises(TypeError, match="PathResolver"):
            tag.set_value(TimerValue())

    def test_set_value_on_array_tag_raises(self, registry):
        tag = Tag("arr", "BOOL", registry, array_size=4)
        with pytest.raises(TypeError, match="PathResolver"):
            tag.set_value(False)
