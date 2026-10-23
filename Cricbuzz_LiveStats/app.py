
"""Cricbuzz LiveStats - Streamlit dashboard."""

import os
import sqlite3
from pathlib import Path
from api.cricbuzz_api import get_players_list
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from services.sql_queries import SQL_QUESTIONS
from services.player_analytics import (
    get_player_statistics,
    get_batting_rankings,
    get_bowling_rankings,
)

from database.db_manager import get_connection
from database.crud_manager import (
    get_players,
    create_player,
    update_player,
    delete_player,
    get_player_stats,
    create_player_stats,
    update_player_stats,
    delete_player_stats,
)

from api.cricbuzz_api import (
    CricbuzzAPIError,
    get_fixtures,
    get_live_matches,
    get_teams,
)

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///database/cricbuzz.db"
).strip()

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------- Helpers --------------------

def records_to_df(records):
    if not records:
        return pd.DataFrame()
    if isinstance(records, dict):
        records = [records]
    if not isinstance(records, list):
        return pd.DataFrame()
    return pd.json_normalize(
        [x if isinstance(x, dict) else {"value": str(x)}
         for x in records],
        sep="_",
    )


def find_column(df, candidates):
    columns = {str(c).lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in columns:
            return columns[candidate.lower()]
    return None


def database_path():
    if not DATABASE_URL.startswith("sqlite:///"):
        raise ValueError(
            "This analytics page currently requires a SQLite DATABASE_URL."
        )
    path = DATABASE_URL.replace("sqlite:///", "", 1)
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return path


def read_sql(query, params=None):
    """Execute a read-only query against the local SQLite database."""
    path = database_path()
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")

    # SQLite URI mode=ro prevents accidental database changes.
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        return pd.read_sql_query(query, conn, params=params or [])
    finally:
        conn.close()


def get_table_names():
    df = read_sql("""
        SELECT name AS table_name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return df["table_name"].tolist()


def show_team_cards(df):
    name_col = find_column(df, ["title", "name", "teamName", "team_name"])
    image_col = find_column(df, ["image", "logo", "teamImage", "team_image"])
    id_col = find_column(df, ["id", "teamId", "team_id"])

    if name_col is None:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    for start in range(0, len(df), 3):
        cols = st.columns(3)
        for offset, (_, row) in enumerate(df.iloc[start:start + 3].iterrows()):
            with cols[offset]:
                with st.container(border=True):
                    if image_col and pd.notna(row.get(image_col)):
                        image_url = str(row[image_col])
                        if image_url.startswith("https://"):
                            st.image(image_url, width=90)
                    st.subheader(str(row[name_col]))
                    if id_col and pd.notna(row.get(id_col)):
                        st.caption(f"Team ID: {row[id_col]}")


# -------------------- Sidebar --------------------

st.sidebar.title("🏏 Cricbuzz LiveStats")
st.sidebar.caption("Cricket insights and SQL analytics")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Home",
        "Teams",
        "Live Matches",
        "Fixtures",
        "Top Player Stats",
        "CRUD Operations",
        "SQL Analytics",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Data supplied by RapidAPI")


# -------------------- Header --------------------

st.title("🏏 Cricbuzz LiveStats")
st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")
st.caption(
    "Explore cricket teams, live matches, upcoming fixtures, "
    "series information, and database analytics."
)
st.divider()


# -------------------- Home --------------------

if page == "Home":
    try:
        teams = read_sql("SELECT COUNT(*) AS n FROM teams").iloc[0]["n"]
    except Exception:
        teams = "Unavailable"

    try:
        fixtures = read_sql("SELECT COUNT(*) AS n FROM fixtures").iloc[0]["n"]
    except Exception:
        fixtures = "Unavailable"

    try:
        series = read_sql("SELECT COUNT(*) AS n FROM series").iloc[0]["n"]
    except Exception:
        series = "Unavailable"

    c1, c2, c3 = st.columns(3)
    c1.metric("Teams in Database", teams)
    c2.metric("Fixture Entries", fixtures)
    c3.metric("Series in Database", series)

    st.markdown("### Explore the dashboard")
    st.info("**Teams:** Browse cricket teams and logos.")
    st.info("**Live Matches:** Check the provider's current live-match data.")
    st.info("**Fixtures:** Filter upcoming and scheduled matches.")
    st.info("**SQL Analytics:** Explore stored data and run read-only queries.")


# -------------------- Teams --------------------

elif page == "Teams":
    st.header("🏏 Cricket Teams")
    if st.button("Refresh Teams", type="primary"):
        st.rerun()

    try:
        df = records_to_df(get_teams())
        if df.empty:
            st.warning("The API returned no team records.")
        else:
            search = st.text_input("Search by team name")
            name_col = find_column(df, ["title", "name", "teamName", "team_name"])
            if search and name_col:
                df = df[df[name_col].astype(str).str.contains(
                    search, case=False, na=False
                )]
            st.success(f"Showing {len(df)} team records.")
            show_team_cards(df)
            st.download_button(
                "Download teams as CSV",
                df.to_csv(index=False).encode("utf-8"),
                "cricbuzz_teams.csv",
                "text/csv",
            )
    except CricbuzzAPIError as exc:
        st.error(str(exc))


# -------------------- Live Matches --------------------

elif page == "Live Matches":
    st.header("🔴 Live Matches")
    if st.button("Refresh Live Matches", type="primary"):
        st.rerun()

    try:
        df = records_to_df(get_live_matches())
        if df.empty:
            st.info(
                "The API returned no live-match records. This can happen "
                "when no matches are live or the provider has no live data."
            )
        else:
            st.success(f"Received {len(df)} records.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download live matches as CSV",
                df.to_csv(index=False).encode("utf-8"),
                "cricbuzz_live_matches.csv",
                "text/csv",
            )
    except CricbuzzAPIError as exc:
        st.error(str(exc))


# -------------------- Fixtures --------------------

elif page == "Fixtures":
    st.header("📅 Fixtures")

    try:
        df = records_to_df(get_fixtures())
        if df.empty:
            st.info("No fixtures were returned by the API.")
        else:
            st.success(f"Loaded {len(df)} schedule entries.")

            team_cols = [
                c for c in ["team1", "team2"] if c in df.columns
            ]
            format_col = find_column(df, ["format"])
            country_col = find_column(df, ["country"])
            series_col = find_column(df, ["series"])

            c1, c2, c3 = st.columns(3)
            if format_col:
                formats = sorted(df[format_col].dropna().astype(str).unique())
                selected_format = c1.selectbox(
                    "Match format", ["All"] + formats
                )
                if selected_format != "All":
                    df = df[df[format_col].astype(str) == selected_format]

            if country_col:
                countries = sorted(df[country_col].dropna().astype(str).unique())
                selected_country = c2.selectbox(
                    "Country", ["All"] + countries
                )
                if selected_country != "All":
                    df = df[df[country_col].astype(str) == selected_country]

            search = c3.text_input("Search teams or series")
            if search:
                searchable = team_cols + (
                    [series_col] if series_col else []
                )
                if searchable:
                    mask = pd.Series(False, index=df.index)
                    for col in searchable:
                        mask |= df[col].astype(str).str.contains(
                            search, case=False, na=False
                        )
                    df = df[mask]

            st.caption(f"{len(df)} entries match your filters.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download filtered fixtures as CSV",
                df.to_csv(index=False).encode("utf-8"),
                "cricbuzz_fixtures.csv",
                "text/csv",
            )
    except CricbuzzAPIError as exc:
        st.error(str(exc))


# -------------------- CRUD Operations --------------------

elif page == "CRUD Operations":
    st.header("🛠️ Player CRUD Operations")
    st.caption("Manage locally maintained player records and match statistics.")

    with get_connection() as conn:
        teams = conn.execute(
            "SELECT id, title FROM teams ORDER BY title"
        ).fetchall()

        fixtures = conn.execute(
            """
            SELECT fixture_id, date, team1, team2, match
            FROM fixtures
            ORDER BY date
            """
        ).fetchall()

    team_options = {"No team": None}
    team_options.update({row["title"]: row["id"] for row in teams})

    team_labels = list(team_options.keys())

    tab_create, tab_view, tab_edit, tab_delete, tab_stats = st.tabs(
        ["Create", "View", "Update", "Delete", "Match Stats"]
    )

    with tab_create:
        st.subheader("Add Player")

        with st.form("create_player_form"):
            name = st.text_input("Player name")
            team_label = st.selectbox("Team", team_labels)
            role = st.selectbox(
                "Role",
                ["Unknown", "Batter", "Bowler", "All-rounder", "Wicketkeeper"],
            )
            batting_style = st.text_input("Batting style (optional)")
            bowling_style = st.text_input("Bowling style (optional)")
            country = st.text_input("Country (optional)")
            submitted = st.form_submit_button("Create Player")

        if submitted:
            try:
                player_id = create_player(
                    name=name,
                    team_id=team_options[team_label],
                    role=None if role == "Unknown" else role,
                    batting_style=batting_style,
                    bowling_style=bowling_style,
                    country=country,
                )
                st.success(f"Player created successfully. ID: {player_id}")
            except Exception as exc:
                st.error(f"Could not create player: {exc}")

    with tab_view:
        st.subheader("Search Players")
        search = st.text_input("Search by player name", key="view_search")
        players = get_players(search)

        if players:
            st.dataframe(
                [dict(row) for row in players],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No player records found.")

    with tab_edit:
        st.subheader("Update Player")

        players = get_players()
        if not players:
            st.info("Create a player before trying to update one.")
        else:
            player_map = {
                f'{p["name"]} (ID: {p["player_id"]})': p
                for p in players
            }
            selected_label = st.selectbox(
                "Choose player to edit", list(player_map.keys())
            )
            selected = player_map[selected_label]

            with st.form("update_player_form"):
                new_name = st.text_input("Player name", value=selected["name"])

                current_team = selected["team_id"]
                default_team_label = next(
                    (
                        label for label, team_id in team_options.items()
                        if team_id == current_team
                    ),
                    "No team",
                )
                new_team_label = st.selectbox(
                    "Team",
                    team_labels,
                    index=team_labels.index(default_team_label),
                )
                role_options = [
                    "Unknown", "Batter", "Bowler",
                    "All-rounder", "Wicketkeeper",
                ]
                current_role = selected["role"] or "Unknown"
                if current_role not in role_options:
                    role_options.append(current_role)

                new_role = st.selectbox(
                    "Role",
                    role_options,
                    index=role_options.index(current_role),
                )
                new_batting = st.text_input(
                    "Batting style",
                    value=selected["batting_style"] or "",
                )
                new_bowling = st.text_input(
                    "Bowling style",
                    value=selected["bowling_style"] or "",
                )
                new_country = st.text_input(
                    "Country",
                    value=selected["country"] or "",
                )
                update_submitted = st.form_submit_button("Save Changes")

            if update_submitted:
                try:
                    update_player(
                        selected["player_id"],
                        new_name,
                        team_options[new_team_label],
                        None if new_role == "Unknown" else new_role,
                        new_batting,
                        new_bowling,
                        new_country,
                    )
                    st.success("Player updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update player: {exc}")

    with tab_delete:
        st.subheader("Delete Player")

        players = get_players()
        if not players:
            st.info("There are no players to delete.")
        else:
            delete_map = {
                f'{p["name"]} (ID: {p["player_id"]})': p["player_id"]
                for p in players
            }
            delete_label = st.selectbox(
                "Choose player", list(delete_map.keys())
            )
            confirm_delete = st.checkbox(
                "I confirm that I want to delete this player."
            )

            if st.button("Delete Selected Player", type="primary"):
                if not confirm_delete:
                    st.warning("Please confirm before deleting.")
                else:
                    try:
                        delete_player(delete_map[delete_label])
                        st.success("Player deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not delete player: {exc}")

    with tab_stats:
        st.subheader("Record Match Statistics")
        players = get_players()

        if not players:
            st.info("Create a player before adding match statistics.")
        else:
            player_map = {
                f'{p["name"]} (ID: {p["player_id"]})': p["player_id"]
                for p in players
            }
            stat_player_label = st.selectbox(
                "Player", list(player_map.keys()), key="stat_player"
            )

            fixture_options = {"No linked fixture": None}
            fixture_options.update({
                (
                    f'{f["date"]} | {f["team1"]} vs {f["team2"]} '
                    f'| {f["match"]} (ID: {f["fixture_id"]})'
                ): f["fixture_id"]
                for f in fixtures
            })
            fixture_label = st.selectbox(
                "Fixture", list(fixture_options.keys())
            )

            with st.form("create_stats_form"):
                match_format = st.selectbox(
                    "Format", ["TEST", "ODI", "T20", "T20I", "Other"]
                )
                runs = st.number_input("Runs", min_value=0, step=1)
                balls = st.number_input("Balls faced", min_value=0, step=1)
                fours = st.number_input("Fours", min_value=0, step=1)
                sixes = st.number_input("Sixes", min_value=0, step=1)
                wickets = st.number_input("Wickets", min_value=0, step=1)
                overs = st.number_input(
                    "Overs bowled", min_value=0.0, step=0.1
                )
                conceded = st.number_input(
                    "Runs conceded", min_value=0, step=1
                )
                catches = st.number_input("Catches", min_value=0, step=1)
                stats_submitted = st.form_submit_button("Save Match Stats")

            if stats_submitted:
                try:
                    stat_id = create_player_stats(
                        player_id=player_map[stat_player_label],
                        fixture_id=fixture_options[fixture_label],
                        match_format=match_format,
                        runs=int(runs),
                        balls_faced=int(balls),
                        fours=int(fours),
                        sixes=int(sixes),
                        wickets=int(wickets),
                        overs_bowled=float(overs),
                        runs_conceded=int(conceded),
                        catches=int(catches),
                    )
                    st.success(f"Statistics saved. Record ID: {stat_id}")
                except Exception as exc:
                    st.error(f"Could not save statistics: {exc}")

        st.markdown("### Saved Match Statistics")
        stats = get_player_stats()

        if stats:
            stats_df = pd.DataFrame([dict(row) for row in stats])
            st.dataframe(
                stats_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No player match statistics have been entered yet.")


# -------------------- Top Player Stats --------------------
elif page == "Top Player Stats":
    st.header("🏏 Top Player Stats")
    st.caption(
        "Database rankings calculated from locally saved match statistics. "
        "These are not verified Cricbuzz API rankings."
    )

    stats_df = get_player_statistics()

    if stats_df.empty:
        st.info(
            "No player statistics are available yet. "
            "Add records under CRUD Operations → Match Stats."
        )
    else:
        batting_df = get_batting_rankings()
        bowling_df = get_bowling_rankings()

        # Filters
        available_formats = sorted(
            stats_df["format"].dropna().astype(str).unique().tolist()
        )

        selected_format = st.selectbox(
            "Filter by match format",
            ["All formats"] + available_formats,
        )

        if selected_format != "All formats":
            stats_df = stats_df[
                stats_df["format"].astype(str) == selected_format
            ]

            player_ids = stats_df["player_id"].unique()
            batting_df = batting_df[
                batting_df["player_id"].isin(player_ids)
            ]
            bowling_df = bowling_df[
                bowling_df["player_id"].isin(player_ids)
            ]

        # Summary metrics
        total_players = stats_df["player_id"].nunique()
        total_runs = int(stats_df["runs"].fillna(0).sum())
        total_wickets = int(stats_df["wickets"].fillna(0).sum())

        col1, col2, col3 = st.columns(3)
        col1.metric("Players", total_players)
        col2.metric("Recorded Runs", total_runs)
        col3.metric("Recorded Wickets", total_wickets)

        batting_tab, bowling_tab, records_tab = st.tabs(
            ["🏏 Batting Rankings", "🎯 Bowling Rankings", "📋 Saved Records"]
        )

        with batting_tab:
            st.subheader("Most Runs")

            filtered_batting = batting_df.copy()

            if selected_format != "All formats":
                filtered_batting = (
                    stats_df.groupby(
                        ["player_id", "player_name"], as_index=False
                    )
                    .agg(
                        matches_recorded=("stat_id", "nunique"),
                        total_runs=("runs", "sum"),
                        balls_faced=("balls_faced", "sum"),
                        fours=("fours", "sum"),
                        sixes=("sixes", "sum"),
                    )
                )

                filtered_batting["strike_rate"] = (
                    filtered_batting["total_runs"]
                    .div(filtered_batting["balls_faced"].replace(0, float("nan")))
                    .mul(100)
                ).fillna(0).round(2)

                filtered_batting = filtered_batting.sort_values(
                    "total_runs", ascending=False
                )

            st.dataframe(
                filtered_batting,
                use_container_width=True,
                hide_index=True,
            )

            if not filtered_batting.empty:
                chart_df = filtered_batting.head(10).set_index("player_name")
                st.bar_chart(chart_df["total_runs"])

        with bowling_tab:
            st.subheader("Most Wickets")

            filtered_bowling = bowling_df.copy()

            if selected_format != "All formats":
                filtered_bowling = (
                    stats_df.groupby(
                        ["player_id", "player_name"], as_index=False
                    )
                    .agg(
                        matches_recorded=("stat_id", "nunique"),
                        wickets=("wickets", "sum"),
                        runs_conceded=("runs_conceded", "sum"),
                    )
                )

                filtered_bowling = filtered_bowling.sort_values(
                    ["wickets", "runs_conceded"],
                    ascending=[False, True],
                )

            st.dataframe(
                filtered_bowling,
                use_container_width=True,
                hide_index=True,
            )

            if not filtered_bowling.empty:
                chart_df = filtered_bowling.head(10).set_index("player_name")
                st.bar_chart(chart_df["wickets"])

        with records_tab:
            st.subheader("Saved Match Statistics")
            st.dataframe(
                stats_df,
                use_container_width=True,
                hide_index=True,
            )


# -------------------- SQL Analytics --------------------

elif page == "SQL Analytics":
    st.header("🗄️ SQL Analytics")
    
    st.markdown("### 📚 Predefined SQL Questions")

    difficulty = st.selectbox(
        "Choose difficulty",
        ["All", "Easy", "Medium", "Hard"],
        key="sql_difficulty",
    )

    available_questions = [
        item for item in SQL_QUESTIONS
        if difficulty == "All"
        or item["difficulty"] == difficulty
    ]

    selected_question = st.selectbox(
        "Choose a SQL question",
        available_questions,
        format_func=lambda item: (
            f'Q{item["id"]}. [{item["difficulty"]}] '
            f'{item["question"]}'
        ),
        key="sql_question",
    )

    with st.expander("View SQL query"):
        st.code(selected_question["sql"], language="sql")

    if st.button("Run Selected Question", type="primary"):
        try:
            result = read_sql(selected_question["sql"])

            st.success(
                f'Question {selected_question["id"]}: '
                f'{len(result)} rows returned.'
            )

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Download answer as CSV",
                result.to_csv(index=False).encode("utf-8"),
                f'sql_question_{selected_question["id"]}.csv',
                "text/csv",
                key=f'sql_download_{selected_question["id"]}',
            )

        except Exception as exc:
            st.error(f"Query failed: {exc}")

    st.divider()

    try:
        tables = get_table_names()
        if not tables:
            st.info("The database has no tables yet.")
        else:
            counts = {}
            for table in tables:
                safe_table = table.replace('"', '""')
                result = read_sql(
                    f'SELECT COUNT(*) AS total FROM "{safe_table}"'
                )
                counts[table] = int(result.iloc[0]["total"])

            metrics = st.columns(len(counts))
            for col, (table, count) in zip(metrics, counts.items()):
                col.metric(table.title(), count)

            st.markdown("### Table preview")
            selected_table = st.selectbox("Choose a table", tables)
            safe_table = selected_table.replace('"', '""')
            preview = read_sql(
                f'SELECT * FROM "{safe_table}" LIMIT 100'
            )
            st.dataframe(preview, use_container_width=True, hide_index=True)
            st.download_button(
                f"Download {selected_table} as CSV",
                preview.to_csv(index=False).encode("utf-8"),
                f"{selected_table}.csv",
                "text/csv",
            )

            st.divider()
            st.markdown("### Fixture analytics")

            try:
                fixtures = read_sql("SELECT * FROM fixtures")
            except Exception:
                fixtures = pd.DataFrame()

            if fixtures.empty:
                st.info("No fixture records are stored yet.")
            else:
                a, b = st.columns(2)

                if "format" in fixtures.columns:
                    format_counts = (
                        fixtures["format"].fillna("Unknown")
                        .value_counts()
                        .rename_axis("Format")
                        .reset_index(name="Fixtures")
                    )
                    fig = px.bar(
                        format_counts, x="Format", y="Fixtures",
                        title="Schedule Entries by Format",
                        text="Fixtures",
                    )
                    a.plotly_chart(fig, use_container_width=True)

                if "country" in fixtures.columns:
                    country_counts = (
                        fixtures["country"].fillna("Unknown")
                        .value_counts()
                        .head(10)
                        .rename_axis("Country")
                        .reset_index(name="Fixtures")
                    )
                    fig = px.bar(
                        country_counts, x="Country", y="Fixtures",
                        title="Top 10 Countries by Schedule Entries",
                        text="Fixtures",
                    )
                    b.plotly_chart(fig, use_container_width=True)

                if "series" in fixtures.columns:
                    series_counts = (
                        fixtures["series"].fillna("Unknown")
                        .value_counts()
                        .head(10)
                        .rename_axis("Series")
                        .reset_index(name="Entries")
                    )
                    fig = px.bar(
                        series_counts, x="Entries", y="Series",
                        orientation="h",
                        title="Top 10 Series by Schedule Entries",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("### Run a read-only SQL query")
            st.caption(
                "Only one SELECT statement is accepted. "
                "Data-changing SQL is not allowed."
            )
            query = st.text_area(
                "SQL query",
                value="SELECT team1, team2, date, format, venue "
                      "FROM fixtures LIMIT 10;",
                height=110,
            )

            if st.button("Run SQL Query", type="primary"):
                cleaned = query.strip()
                # Permit a single read-only SELECT or WITH query.
                normalized = cleaned.rstrip(";").strip()
                forbidden = [
                    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
                    "CREATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
                ]
                upper = normalized.upper()
                if not (upper.startswith("SELECT ") or upper.startswith("WITH ")):
                    st.error("Only SELECT or read-only WITH queries are allowed.")
                elif ";" in normalized:
                    st.error("Please run one SQL statement at a time.")
                elif any(word in upper.split() for word in forbidden):
                    st.error("Data-changing or administrative SQL is blocked.")
                else:
                    try:
                        result = read_sql(normalized)
                        st.success(f"Query returned {len(result)} rows.")
                        st.dataframe(
                            result, use_container_width=True, hide_index=True
                        )
                        st.download_button(
                            "Download query result as CSV",
                            result.to_csv(index=False).encode("utf-8"),
                            "sql_query_result.csv",
                            "text/csv",
                        )
                    except Exception as exc:
                        st.error(f"SQL query failed: {exc}")

    except Exception as exc:
        st.error(f"Could not load SQLite analytics: {exc}")


st.divider()
st.caption(
    "Cricbuzz LiveStats | Data availability depends on the RapidAPI provider."
)
