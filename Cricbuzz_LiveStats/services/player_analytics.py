
"""Player analytics calculated from locally stored match statistics."""

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "cricbuzz.db"


def get_player_statistics():
    """Return saved player performances joined to player names."""

    query = """
        SELECT
            p.player_id,
            p.name AS player_name,
            p.country,
            p.team_id,
            s.stat_id,
            s.format,
            s.runs,
            s.balls_faced,
            s.fours,
            s.sixes,
            s.wickets,
            s.overs_bowled,
            s.runs_conceded,
            s.catches,
            f.date AS fixture_date,
            f.match AS match_description,
            f.team1,
            f.team2
        FROM player_match_stats AS s
        INNER JOIN players AS p
            ON p.player_id = s.player_id
        LEFT JOIN fixtures AS f
            ON f.fixture_id = s.fixture_id
        ORDER BY s.runs DESC
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(query, connection)


def get_batting_rankings():
    """Rank players by total recorded runs and calculate strike rate."""

    df = get_player_statistics()

    if df.empty:
        return df

    df["runs"] = pd.to_numeric(df["runs"], errors="coerce").fillna(0)
    df["balls_faced"] = (
        pd.to_numeric(df["balls_faced"], errors="coerce").fillna(0)
    )
    df["fours"] = pd.to_numeric(df["fours"], errors="coerce").fillna(0)
    df["sixes"] = pd.to_numeric(df["sixes"], errors="coerce").fillna(0)

    batting = (
        df.groupby(["player_id", "player_name"], as_index=False)
        .agg(
            matches_recorded=("stat_id", "nunique"),
            total_runs=("runs", "sum"),
            balls_faced=("balls_faced", "sum"),
            fours=("fours", "sum"),
            sixes=("sixes", "sum"),
        )
    )

    batting["strike_rate"] = 0.0
    valid_balls = batting["balls_faced"] > 0

    batting.loc[valid_balls, "strike_rate"] = (
        batting.loc[valid_balls, "total_runs"]
        / batting.loc[valid_balls, "balls_faced"]
        * 100
    )

    return batting.sort_values(
        ["total_runs", "strike_rate"],
        ascending=[False, False],
    ).reset_index(drop=True)


def get_bowling_rankings():
    """Rank players by total recorded wickets."""

    df = get_player_statistics()

    if df.empty:
        return df

    df["wickets"] = pd.to_numeric(
        df["wickets"], errors="coerce"
    ).fillna(0)

    df["runs_conceded"] = pd.to_numeric(
        df["runs_conceded"], errors="coerce"
    ).fillna(0)

    bowling = (
        df.groupby(["player_id", "player_name"], as_index=False)
        .agg(
            matches_recorded=("stat_id", "nunique"),
            wickets=("wickets", "sum"),
            runs_conceded=("runs_conceded", "sum"),
        )
    )

    return bowling.sort_values(
        ["wickets", "runs_conceded"],
        ascending=[False, True],
    ).reset_index(drop=True)
