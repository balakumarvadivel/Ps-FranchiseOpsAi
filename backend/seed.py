"""
Database seed runner
----------------------
Usage:
    python seed.py            # create schema (if not present) + seed demo data
    python seed.py --reset    # DROP and recreate everything, then seed

Safe to re-run: schema.sql uses CREATE TABLE (fails silently if tables
already exist, unless --reset is passed) and every INSERT in seed.sql uses
ON CONFLICT DO NOTHING or an idempotent UPDATE, so running this multiple
times does not create duplicate rows.

Reads DATABASE_URL from the same .env the FastAPI app uses (via
app.config.settings), so there's exactly one place connection details are
configured — not a second copy of the DB URL living only in this script.
"""
import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parent))
from app.config import settings  # noqa: E402

DATABASE_DIR = Path(__file__).parent.parent / "database"
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
SEED_FILE = DATABASE_DIR / "seed.sql"


def run_sql_file(engine, path: Path, label: str):
    if not path.exists():
        print(f"  ✗ {label} not found at {path}")
        sys.exit(1)

    sql = path.read_text()
    print(f"  Running {label} ({len(sql.splitlines())} lines)...")
    with engine.begin() as conn:
        # Postgres allows multiple ;-separated statements in one execute()
        # via psycopg2's default driver when passed as a single text() block.
        conn.execute(text(sql))
    print(f"  ✓ {label} applied")


def reset_database(engine):
    print("  Dropping all tables (CASCADE)...")
    with engine.begin() as conn:
        conn.execute(text("""
            DO $$ DECLARE r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
    print("  ✓ Database reset")


def main():
    parser = argparse.ArgumentParser(description="Seed the FranchiseOps AI database")
    parser.add_argument("--reset", action="store_true", help="Drop all tables before recreating and seeding")
    args = parser.parse_args()

    print(f"Connecting to: {settings.DATABASE_URL.split('@')[-1]}")  # don't print credentials
    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        print(f"✗ Could not connect to the database: {exc}")
        print("  Check DATABASE_URL in your .env and that PostgreSQL is running.")
        sys.exit(1)

    print("✓ Database connection OK\n")

    if args.reset:
        reset_database(engine)

    print("\n1. Applying schema...")
    run_sql_file(engine, SCHEMA_FILE, "schema.sql")

    print("\n2. Seeding demo data...")
    run_sql_file(engine, SEED_FILE, "seed.sql")

    print("\n✓ Done. Register a user via POST /api/v1/auth/register to start using the app.")


if __name__ == "__main__":
    main()
