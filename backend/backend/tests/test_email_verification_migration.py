import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text


def test_existing_users_are_grandfathered_as_email_verified():
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "20260929_email_verification_and_otp_purposes.py"
    )
    spec = importlib.util.spec_from_file_location("email_verification_migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))"))
        connection.execute(text("INSERT INTO users (email) VALUES ('existing@mteja.ai')"))
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()
        verified = connection.execute(text("SELECT email_verified FROM users")).scalar_one()
        assert bool(verified) is True