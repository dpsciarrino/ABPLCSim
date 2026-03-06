# db/database.py
#
# Responsibilities:
#   - Create the SQLAlchemy engine from DATABASE_URL env variable
#   - Provide a session factory (SessionLocal) for use in API routes
#   - Declare the Base class that all ORM models inherit from
#   - Provide a get_db() dependency for FastAPI route injection
#
# Migration note: Swapping SQLite → PostgreSQL requires only changing
# DATABASE_URL in .env.production. No code changes needed here or in models.py
#
# Dependencies: sqlalchemy, python-dotenv
#
# TODO: Implement engine, SessionLocal, Base, get_db

