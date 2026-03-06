# tests/test_path_resolver.py
#
# Test specification for engine.path_resolver
# All tests are written before implementation (TDD).
#
# Run with: pytest tests/test_path_resolver.py -v

import pytest

# from engine.path_resolver import tokenize, resolve_get, resolve_set, NameToken, IndexToken
# from engine.tag import Tag, TimerValue, StructInstance, ArrayInstance
# from engine.type_registry import TypeRegistry


# ── Tokenizer ─────────────────────────────────────────────────────────────────

class TestTokenize:
    def test_simple_name(self):
        """'valve_open' → [NameToken('valve_open')]"""
        raise NotImplementedError

    def test_struct_member(self):
        """'MyTimer.ACC' → [NameToken('MyTimer'), NameToken('ACC')]"""
        raise NotImplementedError

    def test_array_index(self):
        """'valves[3]' → [NameToken('valves'), IndexToken(3)]"""
        raise NotImplementedError

    def test_array_then_member(self):
        """'motors[2].Running' → [NameToken('motors'), IndexToken(2), NameToken('Running')]"""
        raise NotImplementedError

    def test_array_nested_struct_member(self):
        """'motors[2].RunTimer.ACC' → [NameToken('motors'), IndexToken(2),
                                        NameToken('RunTimer'), NameToken('ACC')]"""
        raise NotImplementedError

    def test_empty_path_raises(self):
        raise NotImplementedError

    def test_invalid_syntax_raises(self):
        """'motors[].Running' or 'motors.[2]' should raise."""
        raise NotImplementedError


# ── resolve_get ───────────────────────────────────────────────────────────────

class TestResolveGet:
    def test_primitive_tag(self):
        """Resolving a BOOL tag returns its value directly."""
        raise NotImplementedError

    def test_timer_member_acc(self):
        """Resolving 'MyTimer.ACC' returns the ACC integer value."""
        raise NotImplementedError

    def test_timer_member_dn(self):
        """Resolving 'MyTimer.DN' returns the DN bool value."""
        raise NotImplementedError

    def test_array_index(self):
        """Resolving 'valves[2]' returns the element at index 2."""
        raise NotImplementedError

    def test_array_of_udt_member(self):
        """Resolving 'motors[1].Running' returns the Running field of element 1."""
        raise NotImplementedError

    def test_array_of_udt_nested_timer_member(self):
        """Resolving 'motors[0].RunTimer.ACC' traverses two struct levels."""
        raise NotImplementedError

    def test_out_of_bounds_index_raises(self):
        raise NotImplementedError

    def test_unknown_member_name_raises(self):
        raise NotImplementedError

    def test_index_on_non_array_raises(self):
        raise NotImplementedError

    def test_member_access_on_primitive_raises(self):
        raise NotImplementedError


# ── resolve_set ───────────────────────────────────────────────────────────────

class TestResolveSet:
    def test_set_primitive_tag(self):
        raise NotImplementedError

    def test_set_timer_member(self):
        """Setting 'MyTimer.PRE' to 5000 updates only PRE; other members unchanged."""
        raise NotImplementedError

    def test_set_array_element(self):
        """Setting 'valves[3]' updates only index 3; other elements unchanged."""
        raise NotImplementedError

    def test_set_udt_member_in_array(self):
        raise NotImplementedError

    def test_set_wrong_type_raises(self):
        """Writing a float to a DINT path must raise a type error."""
        raise NotImplementedError

    def test_set_bool_with_integer_one_accepted(self):
        """Writing 1 to a BOOL path must be accepted."""
        raise NotImplementedError

    def test_set_out_of_range_sint_raises(self):
        raise NotImplementedError
