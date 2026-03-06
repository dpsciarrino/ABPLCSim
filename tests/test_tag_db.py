# tests/test_tag_db.py
#
# Test specification for engine.tag_db
# All tests are written before implementation (TDD).
#
# Run with: pytest tests/test_tag_db.py -v

import pytest

# from engine.tag_db import TagDB
# from engine.tag import Tag
# from engine.type_registry import TypeRegistry


class TestTagDBRegistration:
    def test_register_tag_succeeds(self):
        raise NotImplementedError

    def test_register_duplicate_name_raises(self):
        raise NotImplementedError

    def test_exists_returns_true_for_registered_tag(self):
        raise NotImplementedError

    def test_exists_returns_false_for_unknown_tag(self):
        raise NotImplementedError


class TestTagDBGetSet:
    def test_get_primitive_returns_default_value(self):
        raise NotImplementedError

    def test_set_then_get_returns_updated_value(self):
        raise NotImplementedError

    def test_set_struct_member_via_dot_path(self):
        """Setting 'MyTimer.PRE' updates only PRE; rest of timer unchanged."""
        raise NotImplementedError

    def test_set_array_element_via_index_path(self):
        raise NotImplementedError

    def test_get_nonexistent_root_tag_raises(self):
        raise NotImplementedError

    def test_set_wrong_type_raises(self):
        raise NotImplementedError


class TestTagDBSnapshot:
    def test_all_tags_returns_all_registered_tags(self):
        raise NotImplementedError

    def test_all_tags_is_a_snapshot_not_live_reference(self):
        """Modifying the returned dict must not affect the TagDB."""
        raise NotImplementedError
