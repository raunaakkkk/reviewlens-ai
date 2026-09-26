from sqlalchemy import text

from backend.database import engine


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - POSTGRESQL CONNECTION TEST")
    print("=" * 60)

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT current_database(), version();")
            )

            database_name, version = result.fetchone()

            print("\nDatabase:", database_name)
            print("PostgreSQL:", version.split(",")[0])
            print("\nConnection successful.")

    except Exception as exc:

        print("\nConnection failed:")
        print(exc)

    print("\n" + "=" * 60)