# engine/instructions/bit_logic.py
#
# Instructions: XIC, XIO, OTE, OTL, OTU, ONS
#
# All instructions are pure functions:
#   (tag_db: TagDB, operands: dict, scan_timestamp: float) → rung_continuity: bool
#
# No instruction may call time.time(), write to disk, or hold internal state.
# All state reads and writes go through tag_db.get() and tag_db.set().
#
# XIC (Examine If Closed)  — returns True if tag is True
# XIO (Examine If Open)    — returns True if tag is False
# OTE (Output Energize)    — sets tag to rung_in value; returns rung_in
# OTL (Output Latch)       — sets tag True if rung_in True; returns rung_in
# OTU (Output Unlatch)     — sets tag False if rung_in True; returns rung_in
# ONS (One Shot)           — returns True on first True rung_in; False thereafter until reset
#
# TODO: Implement XIC, XIO, OTE, OTL, OTU, ONS

