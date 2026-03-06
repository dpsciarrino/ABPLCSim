# engine/tag_db.py
#
# Responsibilities:
#   - Implement TagDB, which:
#       * Maintains an internal dict of tag_name → Tag
#       * register(tag: Tag) → None
#           - Accepts an externally created Tag and stores it
#           - Raises error if a tag with the same name already exists
#       * get(path: str) → value
#           - Delegates to PathResolver to traverse the path
#           - Raises error if the root tag name does not exist
#       * set(path: str, value) → None
#           - Delegates to PathResolver to traverse and write
#           - Type validation is enforced inside PathResolver
#       * exists(tag_name: str) → bool
#       * all_tags() → dict[str, Tag]
#           - Returns a snapshot of all registered tags (used by scan engine)
#
# Dependencies: engine.tag, engine.path_resolver, engine.type_registry
#
# TODO: Implement TagDB

