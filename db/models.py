# db/models.py
#
# ORM Models (SQLAlchemy):
#
#   User
#     - id:           Integer, primary key
#     - username:     String, unique, indexed
#     - email:        String, unique
#     - hashed_password: String  (never store plaintext)
#     - created_at:   DateTime
#     - last_login:   DateTime, nullable
#
#   Program
#     - id:           Integer, primary key
#     - owner_id:     Integer, ForeignKey → User.id
#     - name:         String
#     - l5x_content:  Text  (raw XML content of the .L5X file)
#     - uploaded_at:  DateTime
#
#   SessionMeta
#     - id:           Integer, primary key
#     - user_id:      Integer, ForeignKey → User.id, unique
#     - last_active:  DateTime  (updated on every authenticated request)
#
# Dependencies: db.database (Base), sqlalchemy
#
# TODO: Implement User, Program, SessionMeta

