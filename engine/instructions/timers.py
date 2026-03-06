# engine/instructions/timers.py
#
# Instructions: TON, TOF, RTO
#
# All instructions are pure functions:
#   (tag_db: TagDB, operands: dict, scan_timestamp: float) → rung_continuity: bool
#
# Timer instructions read and write TimerValue structs via tag_db.
# They never call time.time() directly — all time comparisons use scan_timestamp.
#
# TON (Timer On Delay)
#   - While rung_in True: ACC increments toward PRE; DN sets when ACC >= PRE
#   - When rung_in False: ACC resets to 0, EN and TT clear
#
# TOF (Timer Off Delay)
#   - While rung_in True: DN bit set immediately
#   - When rung_in goes False: ACC increments toward PRE; DN clears when ACC >= PRE
#
# RTO (Retentive Timer On)
#   - Like TON but ACC does not reset when rung goes False
#   - Requires explicit RES instruction to reset
#
# TODO: Implement TON, TOF, RTO

