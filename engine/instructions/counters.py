# engine/instructions/counters.py
#
# Instructions: CTU, CTD, RES
#
# All instructions are pure functions:
#   (tag_db: TagDB, operands: dict, scan_timestamp: float) → rung_continuity: bool
#
# CTU (Count Up)
#   - On rising edge of rung_in: ACC increments by 1
#   - DN bit sets when ACC >= PRE
#   - OV (overflow) sets if ACC exceeds DINT max
#
# CTD (Count Down)
#   - On rising edge of rung_in: ACC decrements by 1
#   - DN bit sets when ACC <= 0
#   - UN (underflow) sets if ACC goes below DINT min
#
# RES (Reset)
#   - Resets ACC to 0 on any TIMER or COUNTER tag when rung_in True
#   - Clears all status bits (DN, TT, EN, OV, UN)
#
# TODO: Implement CTU, CTD, RES

