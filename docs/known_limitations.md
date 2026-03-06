# Known Limitations

This document records behavioral differences between this emulator and a
physical Allen-Bradley ControlLogix controller. These are deliberate
trade-offs, not bugs.

---

## Timer Resolution

**Limitation:** Timer accuracy is subject to drift under CPU load.
**Real PLC behavior:** Hardware timers are interrupt-driven with sub-millisecond accuracy.
**Emulator behavior:** `time.perf_counter()` is used. Drift is negligible at normal
scan rates but may be measurable under heavy CPU load.
**Affected instructions:** TON, TOF, RTO

---

## Array Dimensions

**Limitation:** Only single-dimension arrays are supported in MVP.
**Real PLC behavior:** ControlLogix supports up to 3-dimensional arrays.
**Workaround:** Flatten multi-dimensional arrays to single-dimension where possible.
**Target milestone for fix:** Post-MVP

---

## Integer Overflow Behavior

**Limitation:** Integer overflow raises a Python exception rather than wrapping.
**Real PLC behavior:** ControlLogix wraps on overflow (e.g., DINT max + 1 = DINT min).
**Target milestone for fix:** v1.1+

---

## Motion Instructions

**Limitation:** Motion instructions (MAM, MAS, MSO, etc.) are not implemented.
**Scope decision:** Out of scope for this project.

---

## Program Flow Instructions

**Limitation:** JSR, RET, SBR are not implemented in MVP.
**Target milestone:** v1.1
