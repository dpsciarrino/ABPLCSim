# engine/time_keeper.py
#
# Responsibilities:
#   - Implement TimeKeeper, a daemon thread that maintains a high-resolution
#     wall clock for use by the scan cycle engine.
#   - snapshot() → float
#       * Returns the current timestamp (time.perf_counter()) captured at the
#         top of the last scan. All instructions in the same scan see the same
#         value — this mirrors real PLC behavior.
#   - start() / stop() / pause() / resume()
#   - Supports mock injection for unit testing (advance time without sleeping)
#
# Note: Using time.perf_counter() for high resolution.
#       Drift under CPU load is a known limitation — see docs/known_limitations.md
#
# Dependencies: threading, time (stdlib only)
#
# TODO: Implement TimeKeeper

