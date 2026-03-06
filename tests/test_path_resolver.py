# tests/test_path_resolver.py
#
# Test specification for engine.path_resolver
# All tests are written before implementation (TDD).
#
# Run with: pytest tests/test_path_resolver.py -v
import pytest
from engine.type_registry import TypeRegistry, TypeDefinition, FieldDefinition
from engine.tag import Tag, TimerValue, CounterValue, StructInstance, ArrayInstance
from engine.path_resolver import PathResolver, NameToken, IndexToken


@pytest.fixture
def registry():
    r = TypeRegistry()
    r.register(TypeDefinition(
        name="MotorControl",
        fields=[
            FieldDefinition("Running",  "BOOL"),
            FieldDefinition("Speed",    "DINT"),
            FieldDefinition("RunTimer", "TIMER"),
        ]
    ))
    return r


@pytest.fixture
def resolver(registry):
    return PathResolver(registry)


# ── split_root ────────────────────────────────────────────────────────────────

class TestSplitRoot:
    def test_primitive_path(self, resolver):
        assert resolver.split_root("valve_open") == ("valve_open", "")

    def test_struct_member(self, resolver):
        assert resolver.split_root("MyTimer.ACC") == ("MyTimer", "ACC")

    def test_array_index(self, resolver):
        assert resolver.split_root("motors[2].Running") == ("motors", "[2].Running")

    def test_deep_path(self, resolver):
        assert resolver.split_root("motors[2].RunTimer.ACC") == (
            "motors", "[2].RunTimer.ACC"
        )

    def test_empty_path_raises(self, resolver):
        with pytest.raises(ValueError, match="empty"):
            resolver.split_root("")

    def test_trailing_dot_raises(self, resolver):
        with pytest.raises(ValueError, match="trailing dot"):
            resolver.split_root("MyTimer.")


# ── tokenize ──────────────────────────────────────────────────────────────────

class TestTokenize:
    def test_empty_returns_empty_list(self, resolver):
        assert resolver.tokenize("") == []

    def test_single_name(self, resolver):
        assert resolver.tokenize("ACC") == [NameToken("ACC")]

    def test_two_names(self, resolver):
        assert resolver.tokenize("RunTimer.ACC") == [
            NameToken("RunTimer"), NameToken("ACC")
        ]

    def test_index_only(self, resolver):
        assert resolver.tokenize("[2]") == [IndexToken(2)]

    def test_index_then_name(self, resolver):
        assert resolver.tokenize("[2].Running") == [
            IndexToken(2), NameToken("Running")
        ]

    def test_index_then_two_names(self, resolver):
        assert resolver.tokenize("[2].RunTimer.ACC") == [
            IndexToken(2), NameToken("RunTimer"), NameToken("ACC")
        ]

    def test_trailing_dot_raises(self, resolver):
        with pytest.raises(ValueError, match="trailing dot"):
            resolver.tokenize("ACC.")

    def test_invalid_syntax_raises(self, resolver):
        with pytest.raises(ValueError, match="unexpected characters"):
            resolver.tokenize("[]")


# ── resolve_get ───────────────────────────────────────────────────────────────

class TestResolveGet:
    def test_primitive_tag(self, resolver, registry):
        tag = Tag("valve_open", "BOOL", registry)
        assert resolver.resolve_get(tag, "") is False

    def test_timer_acc(self, resolver, registry):
        tag = Tag("t", "TIMER", registry)
        assert resolver.resolve_get(tag, "ACC") == 0

    def test_timer_dn(self, resolver, registry):
        tag = Tag("t", "TIMER", registry)
        assert resolver.resolve_get(tag, "DN") is False

    def test_array_index(self, resolver, registry):
        tag = Tag("flags", "BOOL", registry, array_size=4)
        assert resolver.resolve_get(tag, "[2]") is False

    def test_udt_member(self, resolver, registry):
        tag = Tag("m", "MotorControl", registry)
        assert resolver.resolve_get(tag, "Running") is False

    def test_udt_member_dint(self, resolver, registry):
        tag = Tag("m", "MotorControl", registry)
        assert resolver.resolve_get(tag, "Speed") == 0

    def test_array_of_udt_member(self, resolver, registry):
        tag = Tag("motors", "MotorControl", registry, array_size=3)
        assert resolver.resolve_get(tag, "[1].Running") is False

    def test_array_of_udt_nested_timer(self, resolver, registry):
        tag = Tag("motors", "MotorControl", registry, array_size=3)
        assert resolver.resolve_get(tag, "[0].RunTimer.ACC") == 0

    def test_out_of_bounds_raises(self, resolver, registry):
        tag = Tag("flags", "BOOL", registry, array_size=4)
        with pytest.raises(IndexError):
            resolver.resolve_get(tag, "[9]")

    def test_unknown_member_raises(self, resolver, registry):
        tag = Tag("t", "TIMER", registry)
        with pytest.raises(KeyError):
            resolver.resolve_get(tag, "BADFIELD")

    def test_index_on_primitive_raises(self, resolver, registry):
        tag = Tag("v", "DINT", registry)
        with pytest.raises(TypeError):
            resolver.resolve_get(tag, "[0]")

    def test_member_on_primitive_raises(self, resolver, registry):
        tag = Tag("v", "DINT", registry)
        with pytest.raises(TypeError):
            resolver.resolve_get(tag, "ACC")


# ── resolve_set ───────────────────────────────────────────────────────────────

class TestResolveSet:
    def test_set_primitive_tag(self, resolver, registry):
        tag = Tag("v", "BOOL", registry)
        resolver.resolve_set(tag, "", True)
        assert tag.get_value() is True

    def test_set_timer_pre(self, resolver, registry):
        tag = Tag("t", "TIMER", registry)
        resolver.resolve_set(tag, "PRE", 5000)
        assert tag.get_value().PRE == 5000

    def test_set_timer_member_does_not_affect_others(self, resolver, registry):
        tag = Tag("t", "TIMER", registry)
        resolver.resolve_set(tag, "PRE", 1000)
        assert tag.get_value().ACC == 0
        assert tag.get_value().DN is False

    def test_set_array_element(self, resolver, registry):
        tag = Tag("flags", "BOOL", registry, array_size=4)
        resolver.resolve_set(tag, "[2]", True)
        assert resolver.resolve_get(tag, "[2]") is True
        assert resolver.resolve_get(tag, "[0]") is False

    def test_set_udt_member_in_array(self, resolver, registry):
        tag = Tag("motors", "MotorControl", registry, array_size=3)
        resolver.resolve_set(tag, "[1].Speed", 1500)
        assert resolver.resolve_get(tag, "[1].Speed") == 1500
        assert resolver.resolve_get(tag, "[0].Speed") == 0

    def test_set_nested_timer_in_array(self, resolver, registry):
        tag = Tag("motors", "MotorControl", registry, array_size=2)
        resolver.resolve_set(tag, "[0].RunTimer.PRE", 3000)
        assert resolver.resolve_get(tag, "[0].RunTimer.PRE") == 3000
        assert resolver.resolve_get(tag, "[1].RunTimer.PRE") == 0

    def test_set_wrong_type_raises(self, resolver, registry):
        tag = Tag("v", "DINT", registry)
        with pytest.raises(TypeError):
            resolver.resolve_set(tag, "", "hello")

    def test_set_bool_with_integer_one(self, resolver, registry):
        tag = Tag("v", "BOOL", registry)
        resolver.resolve_set(tag, "", 1)
        assert tag.get_value() == 1

    def test_set_out_of_range_sint_raises(self, resolver, registry):
        tag = Tag("v", "SINT", registry)
        with pytest.raises(ValueError):
            resolver.resolve_set(tag, "", 999)

    def test_set_struct_leaf_raises(self, resolver, registry):
        """Writing directly to a TIMER member (structured) must raise."""
        tag = Tag("m", "MotorControl", registry)
        with pytest.raises(TypeError, match="structured member"):
            resolver.resolve_set(tag, "RunTimer", TimerValue())