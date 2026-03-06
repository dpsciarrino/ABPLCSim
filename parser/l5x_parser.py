# parser/l5x_parser.py
#
# Responsibilities:
#   - Parse a Studio 5000 .L5X XML export file into internal objects
#   - Extract and register UDT definitions into a TypeRegistry
#   - Extract and create Tag instances for all controller-scoped tags
#   - Extract rung logic and map to instruction objects for the ScanCycleEngine
#   - Handle schema version differences across Studio 5000 releases
#
# Input:  path to a .L5X file (str or Path)
# Output: ParsedProgram dataclass containing TypeRegistry, list[Tag], list[Rung]
#
# Dependencies: lxml, engine.type_registry, engine.tag
#
# TODO: Implement L5XParser, ParsedProgram

