
SQL_QUESTIONS = [
    {
        "id": 1, "difficulty": "Easy",
        "question": "How many teams are stored?",
        "sql": "SELECT COUNT(*) AS total_teams FROM teams;"
    },
    {
        "id": 2, "difficulty": "Easy",
        "question": "Show all teams",
        "sql": "SELECT * FROM teams LIMIT 100;"
    },
    {
        "id": 3, "difficulty": "Easy",
        "question": "How many fixtures are stored?",
        "sql": "SELECT COUNT(*) AS total_fixtures FROM fixtures;"
    },
    {
        "id": 4, "difficulty": "Easy",
        "question": "Show the latest 10 fixtures",
        "sql": "SELECT * FROM fixtures ORDER BY date DESC LIMIT 10;"
    },
    {
        "id": 5, "difficulty": "Easy",
        "question": "Count fixtures by format",
        "sql": "SELECT format, COUNT(*) AS total FROM fixtures GROUP BY format ORDER BY total DESC;"
    },
    {
        "id": 6, "difficulty": "Easy",
        "question": "Count fixtures by country",
        "sql": "SELECT country, COUNT(*) AS total FROM fixtures GROUP BY country ORDER BY total DESC;"
    },
    {
        "id": 7, "difficulty": "Easy",
        "question": "List available series",
        "sql": "SELECT * FROM series LIMIT 100;"
    },
    {
        "id": 8, "difficulty": "Easy",
        "question": "Count saved players",
        "sql": "SELECT COUNT(*) AS total_players FROM players;"
    },
    {
        "id": 9, "difficulty": "Medium",
        "question": "Find fixtures with a known venue",
        "sql": "SELECT match, team1, team2, venue, date FROM fixtures WHERE venue IS NOT NULL AND TRIM(venue) <> '' LIMIT 100;"
    },
    {
        "id": 10, "difficulty": "Medium",
        "question": "Find fixtures where either team is missing",
        "sql": "SELECT match, team1, team2, date FROM fixtures WHERE team1 IS NULL OR team2 IS NULL OR TRIM(team1) = '' OR TRIM(team2) = '' LIMIT 100;"
    },
    {
        "id": 11, "difficulty": "Medium",
        "question": "Count fixtures per series",
        "sql": "SELECT series, COUNT(*) AS fixture_count FROM fixtures GROUP BY series ORDER BY fixture_count DESC LIMIT 20;"
    },
    {
        "id": 12, "difficulty": "Medium",
        "question": "Show fixtures by city",
        "sql": "SELECT city, COUNT(*) AS fixture_count FROM fixtures WHERE city IS NOT NULL GROUP BY city ORDER BY fixture_count DESC LIMIT 20;"
    },
    {
        "id": 13, "difficulty": "Medium",
        "question": "Find duplicate fixture descriptions",
        "sql": "SELECT match, date, COUNT(*) AS copies FROM fixtures GROUP BY match, date HAVING COUNT(*) > 1;"
    },
    {
        "id": 14, "difficulty": "Medium",
        "question": "Count player statistics records",
        "sql": "SELECT COUNT(*) AS total_records FROM player_match_stats;"
    },
    {
        "id": 15, "difficulty": "Medium",
        "question": "Calculate total runs by player",
        "sql": "SELECT player_name, SUM(COALESCE(runs, 0)) AS total_runs FROM player_match_stats GROUP BY player_name ORDER BY total_runs DESC;"
    },
    {
        "id": 16, "difficulty": "Medium",
        "question": "Find players with the most wickets in saved records",
        "sql": "SELECT player_name, SUM(COALESCE(wickets, 0)) AS total_wickets FROM player_match_stats GROUP BY player_name ORDER BY total_wickets DESC LIMIT 10;"
    },
    {
        "id": 17, "difficulty": "Medium",
        "question": "Calculate runs by match format",
        "sql": "SELECT format, SUM(COALESCE(runs, 0)) AS total_runs FROM player_match_stats GROUP BY format ORDER BY total_runs DESC;"
    },
    {
        "id": 18, "difficulty": "Hard",
        "question": "Rank players by total runs",
        "sql": "SELECT player_name, SUM(COALESCE(runs, 0)) AS total_runs, RANK() OVER (ORDER BY SUM(COALESCE(runs, 0)) DESC) AS run_rank FROM player_match_stats GROUP BY player_name;"
    },
    {
        "id": 19, "difficulty": "Hard",
        "question": "Calculate each player's average runs per recorded innings",
        "sql": "SELECT player_name, ROUND(AVG(runs), 2) AS average_runs, COUNT(*) AS innings_recorded FROM player_match_stats GROUP BY player_name ORDER BY average_runs DESC;"
    },
    {
        "id": 20, "difficulty": "Hard",
        "question": "Find each player's highest recorded score",
        "sql": "SELECT player_name, MAX(runs) AS highest_score FROM player_match_stats GROUP BY player_name ORDER BY highest_score DESC;"
    },
    {
        "id": 21, "difficulty": "Hard",
        "question": "Calculate boundary totals by player",
        "sql": "SELECT player_name, SUM(COALESCE(fours, 0)) AS total_fours, SUM(COALESCE(sixes, 0)) AS total_sixes FROM player_match_stats GROUP BY player_name ORDER BY total_sixes DESC;"
    },
    {
        "id": 22, "difficulty": "Hard",
        "question": "Calculate strike rate from saved records",
        "sql": "SELECT player_name, ROUND(100.0 * SUM(COALESCE(runs, 0)) / NULLIF(SUM(COALESCE(balls, 0)), 0), 2) AS strike_rate FROM player_match_stats GROUP BY player_name HAVING SUM(COALESCE(balls, 0)) > 0 ORDER BY strike_rate DESC;"
    },
    {
        "id": 23, "difficulty": "Hard",
        "question": "Show batting records alongside fixture details",
        "sql": "SELECT p.player_name, s.format, s.runs, s.balls, f.date, f.team1, f.team2, f.venue FROM player_match_stats s LEFT JOIN fixtures f ON s.fixture_id = f.fixture_id LEFT JOIN players p ON s.player_id = p.player_id LIMIT 100;"
    },
    {
        "id": 24, "difficulty": "Hard",
        "question": "Compare runs and wickets by player",
        "sql": "SELECT player_name, SUM(COALESCE(runs, 0)) AS total_runs, SUM(COALESCE(wickets, 0)) AS total_wickets FROM player_match_stats GROUP BY player_name ORDER BY total_runs DESC, total_wickets DESC;"
    },
    {
        "id": 25, "difficulty": "Hard",
        "question": "Find players with more than one saved statistics record",
        "sql": "SELECT player_name, COUNT(*) AS records_count, SUM(COALESCE(runs, 0)) AS total_runs FROM player_match_stats GROUP BY player_name HAVING COUNT(*) > 1 ORDER BY records_count DESC;"
    },
]
