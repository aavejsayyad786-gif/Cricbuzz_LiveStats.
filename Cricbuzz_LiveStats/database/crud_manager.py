
"""CRUD functions for players and player match statistics."""

from database.db_manager import get_connection


def get_players(search=""):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT p.*, t.title AS team_name
            FROM players p
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.name LIKE ?
            ORDER BY p.name
            """,
            (f"%{search.strip()}%",),
        ).fetchall()


def create_player(name, team_id=None, role=None,
                  batting_style=None, bowling_style=None, country=None):
    name = name.strip()
    if not name:
        raise ValueError("Player name is required.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO players
                (name, team_id, role, batting_style, bowling_style, country)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name, team_id or None, role or None,
                batting_style or None, bowling_style or None,
                country or None,
            ),
        )
        return cursor.lastrowid


def update_player(player_id, name, team_id=None, role=None,
                  batting_style=None, bowling_style=None, country=None):
    name = name.strip()
    if not name:
        raise ValueError("Player name is required.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE players
            SET name = ?, team_id = ?, role = ?, batting_style = ?,
                bowling_style = ?, country = ?
            WHERE player_id = ?
            """,
            (
                name, team_id or None, role or None,
                batting_style or None, bowling_style or None,
                country or None, player_id,
            ),
        )
        if cursor.rowcount == 0:
            raise ValueError("Player record was not found.")


def delete_player(player_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM players WHERE player_id = ?",
            (player_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("Player record was not found.")


def get_player_stats(player_id=None):
    query = """
        SELECT
            s.stat_id,
            p.name AS player_name,
            f.date AS fixture_date,
            f.team1,
            f.team2,
            s.format,
            s.runs,
            s.balls_faced,
            s.fours,
            s.sixes,
            s.wickets,
            s.overs_bowled,
            s.runs_conceded,
            s.catches
        FROM player_match_stats s
        JOIN players p ON p.player_id = s.player_id
        LEFT JOIN fixtures f ON f.fixture_id = s.fixture_id
    """
    params = ()

    if player_id is not None:
        query += " WHERE s.player_id = ?"
        params = (player_id,)

    query += " ORDER BY s.stat_id DESC"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def create_player_stats(
    player_id, fixture_id, match_format, runs, balls_faced,
    fours, sixes, wickets, overs_bowled, runs_conceded, catches
):
    values = (
        player_id, fixture_id or None, match_format or None,
        runs, balls_faced, fours, sixes, wickets,
        overs_bowled, runs_conceded, catches,
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO player_match_stats (
                player_id, fixture_id, format, runs, balls_faced,
                fours, sixes, wickets, overs_bowled,
                runs_conceded, catches
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        return cursor.lastrowid


def update_player_stats(
    stat_id, player_id, fixture_id, match_format, runs, balls_faced,
    fours, sixes, wickets, overs_bowled, runs_conceded, catches
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE player_match_stats
            SET player_id = ?, fixture_id = ?, format = ?,
                runs = ?, balls_faced = ?, fours = ?, sixes = ?,
                wickets = ?, overs_bowled = ?, runs_conceded = ?,
                catches = ?, updated_at = CURRENT_TIMESTAMP
            WHERE stat_id = ?
            """,
            (
                player_id, fixture_id or None, match_format or None,
                runs, balls_faced, fours, sixes, wickets,
                overs_bowled, runs_conceded, catches, stat_id,
            ),
        )
        if cursor.rowcount == 0:
            raise ValueError("Statistics record was not found.")


def delete_player_stats(stat_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM player_match_stats WHERE stat_id = ?",
            (stat_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("Statistics record was not found.")
