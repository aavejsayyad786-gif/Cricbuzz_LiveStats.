
-- Cricbuzz LiveStats: Database Schema
-- Database: SQLite
-- Safe to run against an existing database.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    image TEXT
);

CREATE TABLE IF NOT EXISTS series (
    title TEXT PRIMARY KEY,
    month TEXT,
    series TEXT,
    dates TEXT,
    url TEXT
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
    runs INTEGER NOT NULL DEFAULT 0 CHECK (runs >= 0),
    balls_faced INTEGER NOT NULL DEFAULT 0 CHECK (balls_faced >= 0),
    fours INTEGER NOT NULL DEFAULT 0 CHECK (fours >= 0),
    sixes INTEGER NOT NULL DEFAULT 0 CHECK (sixes >= 0),
    wickets INTEGER NOT NULL DEFAULT 0 CHECK (wickets >= 0),
    overs_bowled REAL NOT NULL DEFAULT 0
        CHECK (overs_bowled >= 0),
    runs_conceded INTEGER NOT NULL DEFAULT 0
        CHECK (runs_conceded >= 0),
    catches INTEGER NOT NULL DEFAULT 0 CHECK (catches >= 0),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id)
        REFERENCES players(player_id)
        ON DELETE CASCADE,
    FOREIGN KEY (fixture_id)
        REFERENCES fixtures(fixture_id)
        ON DELETE SET NULL
);

-- Indexes to improve common lookup and analytics queries.
CREATE INDEX IF NOT EXISTS idx_players_team_id
    ON players(team_id);

CREATE INDEX IF NOT EXISTS idx_fixtures_date
    ON fixtures(date);

CREATE INDEX IF NOT EXISTS idx_fixtures_format
    ON fixtures(format);

CREATE INDEX IF NOT EXISTS idx_stats_player_id
    ON player_match_stats(player_id);

CREATE INDEX IF NOT EXISTS idx_stats_fixture_id
    ON player_match_stats(fixture_id);

CREATE INDEX IF NOT EXISTS idx_stats_format
    ON player_match_stats(format);
