
"""Database manager for Cricbuzz LiveStats."""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "cricbuzz.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create tables and indexes without deleting existing records."""

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                image TEXT
            );

            CREATE TABLE IF NOT EXISTS fixtures (
                fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                date TEXT,
                series TEXT,
                match TEXT,
                format TEXT,
                team1 TEXT,
                team2 TEXT,
                venue TEXT,
                city TEXT,
                country TEXT,
                start_date TEXT,
                status TEXT,
                UNIQUE(match_id, date, match)
            );

            CREATE TABLE IF NOT EXISTS series (
                title TEXT PRIMARY KEY,
                month TEXT,
                series TEXT,
                dates TEXT,
                url TEXT
            );

            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team_id TEXT,
                role TEXT,
                batting_style TEXT,
                bowling_style TEXT,
                country TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id)
                    REFERENCES teams(id)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS player_match_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                fixture_id INTEGER,
                format TEXT,
                runs INTEGER NOT NULL DEFAULT 0
                    CHECK (runs >= 0),
                balls_faced INTEGER NOT NULL DEFAULT 0
                    CHECK (balls_faced >= 0),
                fours INTEGER NOT NULL DEFAULT 0
                    CHECK (fours >= 0),
                sixes INTEGER NOT NULL DEFAULT 0
                    CHECK (sixes >= 0),
                wickets INTEGER NOT NULL DEFAULT 0
                    CHECK (wickets >= 0),
                overs_bowled REAL NOT NULL DEFAULT 0
                    CHECK (overs_bowled >= 0),
                runs_conceded INTEGER NOT NULL DEFAULT 0
                    CHECK (runs_conceded >= 0),
                catches INTEGER NOT NULL DEFAULT 0
                    CHECK (catches >= 0),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (fixture_id)
                    REFERENCES fixtures(fixture_id)
                    ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_players_name
                ON players(name);

            CREATE INDEX IF NOT EXISTS idx_players_team
                ON players(team_id);

            CREATE INDEX IF NOT EXISTS idx_stats_player
                ON player_match_stats(player_id);

            CREATE INDEX IF NOT EXISTS idx_stats_fixture
                ON player_match_stats(fixture_id);

            CREATE INDEX IF NOT EXISTS idx_fixtures_format
                ON fixtures(format);

            CREATE INDEX IF NOT EXISTS idx_fixtures_country
                ON fixtures(country);
        """)

        # Migrate an older fixtures schema if it used match_id
        # as the primary key. Preserve existing records.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(fixtures)")
        }

        if "fixture_id" not in columns:
            conn.executescript("""
                ALTER TABLE fixtures RENAME TO fixtures_old;

                CREATE TABLE fixtures (
                    fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER,
                    date TEXT,
                    series TEXT,
                    match TEXT,
                    format TEXT,
                    team1 TEXT,
                    team2 TEXT,
                    venue TEXT,
                    city TEXT,
                    country TEXT,
                    start_date TEXT,
                    status TEXT,
                    UNIQUE(match_id, date, match)
                );

                INSERT OR IGNORE INTO fixtures (
                    match_id, date, series, match, format,
                    team1, team2, venue, city, country,
                    start_date, status
                )
                SELECT
                    match_id, date, series, match, format,
                    team1, team2, venue, city, country,
                    start_date, status
                FROM fixtures_old;

                DROP TABLE fixtures_old;
            """)

        # Recreate fixture indexes after a possible migration.
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fixtures_format
            ON fixtures(format)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fixtures_country
            ON fixtures(country)
        """)


def save_records(table, records):
    """Insert or update records received from the API."""

    if table not in {"teams", "fixtures", "series"}:
        raise ValueError("Unsupported API table")

    if not records:
        return 0

    if table == "teams":
        sql = """
            INSERT INTO teams (id, title, image)
            VALUES (:id, :title, :image)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                image = excluded.image
        """

    elif table == "series":
        sql = """
            INSERT INTO series (title, month, series, dates, url)
            VALUES (:title, :month, :series, :dates, :url)
            ON CONFLICT(title) DO UPDATE SET
                month = excluded.month,
                series = excluded.series,
                dates = excluded.dates,
                url = excluded.url
        """

    else:
        sql = """
            INSERT INTO fixtures (
                match_id, date, series, match, format,
                team1, team2, venue, city, country,
                start_date, status
            )
            VALUES (
                :match_id, :date, :series, :match, :format,
                :team1, :team2, :venue, :city, :country,
                :start_date, :status
            )
            ON CONFLICT(match_id, date, match) DO UPDATE SET
                series = excluded.series,
                format = excluded.format,
                team1 = excluded.team1,
                team2 = excluded.team2,
                venue = excluded.venue,
                city = excluded.city,
                country = excluded.country,
                start_date = excluded.start_date,
                status = excluded.status
        """

    with get_connection() as conn:
        conn.executemany(sql, records)

    return len(records)


def get_table_counts():
    """Return record counts for all project tables."""

    tables = (
        "teams",
        "fixtures",
        "series",
        "players",
        "player_match_stats",
    )

    with get_connection() as conn:
        return {
            table: conn.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]
            for table in tables
        }
