# engine/path_resolver.py
#
# Responsibilities:
#   - Define PathToken base and subtypes: NameToken, IndexToken
#   - Implement tokenize(path: str) → list[PathToken]
#       * Splits a path string like "motors[2].RunTimer.ACC" into tokens
#       * NameToken("motors"), IndexToken(2), NameToken("RunTimer"), NameToken("ACC")
#   - Implement resolve_get(tag, tokens) → value
#       * Traverses a Tag's value structure following the token list
#       * Raises errors for: out-of-bounds index, unknown member, index on non-array,
#         member access on non-struct
#   - Implement resolve_set(tag, tokens, value, type_registry) → None
#       * Traverses to the target location and validates type before writing
#       * Raises errors for type mismatches and invalid paths
#
# Note: Single-dimension arrays only for MVP.
#       Multi-dimensional array support is deferred — see docs/known_limitations.md
#
# Dependencies: engine.tag, engine.type_registry
#
# TODO: Implement PathToken, NameToken, IndexToken, tokenize, resolve_get, resolve_set

