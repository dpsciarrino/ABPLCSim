# engine/tag.py
#
# Responsibilities:
#   - Define TimerValue dataclass (PRE, ACC, EN, TT, DN)
#   - Define CounterValue dataclass (PRE, ACC, CU, CD, DN, OV, UN)
#   - Define StructInstance — holds field_name → value for a UDT instance
#   - Define ArrayInstance — holds a fixed-size list of typed elements
#   - Define Tag — the unit stored in TagDB:
#       * name: str
#       * type_name: str  (references a type in the TypeRegistry)
#       * value: any      (TimerValue | CounterValue | StructInstance |
#                          ArrayInstance | bool | int | float)
#   - Tag is created externally and registered with TagDB (Option B pattern)
#   - Default value initialization is handled here, not in TagDB
#
# Dependencies: engine.type_registry
#
# TODO: Implement TimerValue, CounterValue, StructInstance, ArrayInstance, Tag

