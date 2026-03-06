# engine/type_registry.py
#
# Responsibilities:
#   - Define the TagType enum for all supported primitive and structured types
#   - Define FieldDefinition (a single named+typed field within a UDT)
#   - Define TypeDefinition (a named UDT composed of FieldDefinitions)
#   - Implement TypeRegistry, which:
#       * Pre-loads all built-in types (BOOL, SINT, INT, DINT, REAL, TIMER, COUNTER)
#       * Accepts registration of user-defined UDTs
#       * Validates that all field types exist before accepting a UDT
#       * Detects and rejects circular UDT references
#       * Rejects duplicate type name registration
#
# Dependencies: none (this module has no imports from within this project)
#
# TODO: Implement TagType, FieldDefinition, TypeDefinition, TypeRegistry

