
import sys
from pathlib import Path

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.cricbuzz_api import get_teams, get_fixtures, get_series
from database.db_manager import (
    initialize_database,
    save_records,
    get_table_counts,
)


def main():
    initialize_database()

    print("Fetching teams...")
    teams = get_teams()
    print(f"Teams received: {len(teams)}")
    print(f"Teams saved: {save_records('teams', teams)}")

    print("\nFetching fixtures...")
    fixtures = get_fixtures()
    print(f"Fixtures received: {len(fixtures)}")
    print(f"Fixtures saved: {save_records('fixtures', fixtures)}")

    print("\nFetching series...")
    series_records = get_series()
    print(f"Series received: {len(series_records)}")
    print(f"Series saved: {save_records('series', series_records)}")

    print("\nFinal database totals:")
    for table, count in get_table_counts().items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
