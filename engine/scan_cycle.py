# engine/scan_cycle.py
#
# Responsibilities:
#   - Implement ScanCycleEngine, which:
#       * Holds a reference to a TagDB and a TimeKeeper
#       * Executes a loaded program (list of rungs) in a continuous loop
#       * Each scan:
#           1. Input scan  — snapshot virtual inputs into TagDB
#           2. Program scan — execute all rungs sequentially
#           3. Output scan  — write output tags to simulated I/O
#           4. Housekeeping — update scan counter, check watchdog
#       * Captures a single timestamp from TimeKeeper at scan START;
#         passes it to all instructions — no instruction calls time directly
#       * start() / stop() / step() (single scan, for testing)
#
# Dependencies: engine.tag_db, engine.time_keeper, engine.instructions.*
#
# TODO: Implement ScanCycleEngine

