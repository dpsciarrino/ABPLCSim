# db/crud.py
#
# CRUD helper functions — no raw SQL anywhere in API routes.
# All database operations go through these functions.
#
# User operations:
#   create_user(db, username, email, hashed_password) → User
#   get_user_by_username(db, username) → User | None
#   get_user_by_id(db, user_id) → User | None
#   update_last_login(db, user_id) → None
#
# Program operations:
#   create_program(db, owner_id, name, l5x_content) → Program
#   get_programs_by_owner(db, owner_id) → list[Program]
#   get_program_by_id(db, program_id) → Program | None
#   delete_program(db, program_id) → None
#
# SessionMeta operations:
#   upsert_session_meta(db, user_id) → SessionMeta
#   get_session_meta(db, user_id) → SessionMeta | None
#   update_last_active(db, user_id) → None
#
# Dependencies: db.models, sqlalchemy Session
#
# TODO: Implement all CRUD functions

