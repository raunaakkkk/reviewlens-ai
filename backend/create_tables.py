from backend.database import Base, engine
from backend.models import Review


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - DATABASE TABLE CREATION")
    print("=" * 60)

    Base.metadata.create_all(
        bind=engine
    )

    print("\nDatabase tables created successfully.")

    print("\nCreated table:")
    print("- reviews")

    print("\n" + "=" * 60)