# tests/test_tag_db.py
#
# Test specification for engine.tag_db
# All tests are written before implementation (TDD).
#
# Run with: pytest tests/test_tag_db.py -v
import pytest
from engine.type_registry import TypeRegistry, TypeDefinition, FieldDefinition
from engine.tag import Tag, TimerValue
from engine.tag_db import TagDB


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
def db(registry):
    return TagDB(registry)


# ── Registration ──────────────────────────────────────────────────────────────

class TestTagDBRegistration:
    def test_register_tag_succeeds(self, db, registry):
        tag = Tag("valve_open", "BOOL", registry)
        db.register(tag)
        assert db.exists("valve_open")

    def test_register_duplicate_name_raises(self, db, registry):
        tag = Tag("valve_open", "BOOL", registry)
        db.register(tag)
        with pytest.raises(ValueError, match="already registered"):
            db.register(Tag("valve_open", "DINT", registry))

    def test_exists_false_for_unknown_tag(self, db):
        assert db.exists("nonexistent") is False

    def test_register_unregistered_type_raises(self, db, registry):
        """Defensive check — manually bypass Tag constructor to simulate bad tag."""
        tag = Tag("v", "BOOL", registry)
        tag.type_name = "FAKETYPE"          # force an invalid type
        with pytest.raises(ValueError, match="unregistered type"):
            db.register(tag)


# ── get ───────────────────────────────────────────────────────────────────────

class TestTagDBGet:
    def test_get_primitive_default(self, db, registry):
        db.register(Tag("valve_open", "BOOL", registry))
        assert db.get("valve_open") is False

    def test_get_dint_default(self, db, registry):
        db.register(Tag("count", "DINT", registry))
        assert db.get("count") == 0

    def test_get_timer_member(self, db, registry):
        db.register(Tag("t", "TIMER", registry))
        assert db.get("t.ACC") == 0
        assert db.get("t.DN") is False

    def test_get_udt_member(self, db, registry):
        db.register(Tag("motor", "MotorControl", registry))
        assert db.get("motor.Running") is False
        assert db.get("motor.Speed") == 0

    def test_get_array_element(self, db, registry):
        db.register(Tag("flags", "BOOL", registry, array_size=4))
        assert db.get("flags[0]") is False

    def test_get_array_udt_member(self, db, registry):
        db.register(Tag("motors", "MotorControl", registry, array_size=3))
        assert db.get("motors[1].Running") is False

    def test_get_array_nested_timer(self, db, registry):
        db.register(Tag("motors", "MotorControl", registry, array_size=3))
        assert db.get("motors[0].RunTimer.ACC") == 0

    def test_get_nonexistent_root_raises(self, db):
        with pytest.raises(KeyError, match="not registered"):
            db.get("nonexistent")

    def test_get_unknown_member_raises(self, db, registry):
        db.register(Tag("t", "TIMER", registry))
        with pytest.raises(KeyError):
            db.get("t.BADFIELD")

    def test_get_out_of_bounds_raises(self, db, registry):
        db.register(Tag("flags", "BOOL", registry, array_size=4))
        with pytest.raises(IndexError):
            db.get("flags[9]")


# ── set ───────────────────────────────────────────────────────────────────────

class TestTagDBSet:
    def test_set_then_get_primitive(self, db, registry):
        db.register(Tag("valve_open", "BOOL", registry))
        db.set("valve_open", True)
        assert db.get("valve_open") is True

    def test_set_timer_pre(self, db, registry):
        db.register(Tag("t", "TIMER", registry))
        db.set("t.PRE", 5000)
        assert db.get("t.PRE") == 5000
        assert db.get("t.ACC") == 0  # other members unchanged

    def test_set_udt_member(self, db, registry):
        db.register(Tag("motor", "MotorControl", registry))
        db.set("motor.Speed", 1500)
        assert db.get("motor.Speed") == 1500
        assert db.get("motor.Running") is False  # unchanged

    def test_set_array_element(self, db, registry):
        db.register(Tag("flags", "BOOL", registry, array_size=4))
        db.set("flags[2]", True)
        assert db.get("flags[2]") is True
        assert db.get("flags[0]") is False  # unchanged

    def test_set_array_udt_member(self, db, registry):
        db.register(Tag("motors", "MotorControl", registry, array_size=3))
        db.set("motors[1].Speed", 1800)
        assert db.get("motors[1].Speed") == 1800
        assert db.get("motors[0].Speed") == 0  # unchanged

    def test_set_nested_timer_in_array(self, db, registry):
        db.register(Tag("motors", "MotorControl", registry, array_size=2))
        db.set("motors[0].RunTimer.PRE", 3000)
        assert db.get("motors[0].RunTimer.PRE") == 3000
        assert db.get("motors[1].RunTimer.PRE") == 0  # unchanged

    def test_set_wrong_type_raises(self, db, registry):
        db.register(Tag("count", "DINT", registry))
        with pytest.raises(TypeError):
            db.set("count", "hello")

    def test_set_out_of_range_raises(self, db, registry):
        db.register(Tag("v", "SINT", registry))
        with pytest.raises(ValueError):
            db.set("v", 999)

    def test_set_nonexistent_root_raises(self, db):
        with pytest.raises(KeyError, match="not registered"):
            db.set("nonexistent", True)


# ── get_tag and all_tags ──────────────────────────────────────────────────────

class TestTagDBSnapshot:
    def test_get_tag_returns_tag_object(self, db, registry):
        tag = Tag("v", "BOOL", registry)
        db.register(tag)
        assert db.get_tag("v") is tag

    def test_get_tag_nonexistent_raises(self, db):
        with pytest.raises(KeyError, match="not registered"):
            db.get_tag("nonexistent")

    def test_all_tags_returns_all(self, db, registry):
        db.register(Tag("a", "BOOL", registry))
        db.register(Tag("b", "DINT", registry))
        snapshot = db.all_tags()
        assert "a" in snapshot
        assert "b" in snapshot

    def test_all_tags_is_a_copy(self, db, registry):
        db.register(Tag("a", "BOOL", registry))
        snapshot = db.all_tags()
        snapshot["injected"] = None
        assert "injected" not in db.all_tags()