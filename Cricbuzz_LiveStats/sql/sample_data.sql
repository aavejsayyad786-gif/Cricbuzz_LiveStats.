
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- 1. Insert demo teams
INSERT OR IGNORE INTO teams (id, title, image)
VALUES
    ('DEMO_IND', 'India (Demo)', ''),
    ('DEMO_AUS', 'Australia (Demo)', '');

-- 2. Insert demo series
INSERT OR IGNORE INTO series (title, month, series, dates, url)
VALUES (
    'Demo International Series',
    'January 2099',
    'Demo International Series',
    '10 January 2099',
    ''
);

-- 3. Insert demo fixture
INSERT OR IGNORE INTO fixtures (
    match_id, date, series, match, format,
    team1, team2, venue, city, country,
    start_date, status
)
VALUES (
    990001,
    '2099-01-10',
    'Demo International Series',
    'Demo Match 1',
    'ODI',
    'India (Demo)',
    'Australia (Demo)',
    'Demo Stadium',
    'Pune',
    'India',
    '2099-01-10',
    'Demo match - sample data'
);

-- 4. Insert demo players
INSERT OR IGNORE INTO players (
    player_id, name, team_id, role,
    batting_style, bowling_style, country
)
VALUES
(
    990001,
    'Demo Batter',
    'DEMO_IND',
    'Batter',
    'Right-hand bat',
    'Right-arm medium',
    'India'
),
(
    990002,
    'Demo All-Rounder',
    'DEMO_AUS',
    'All-rounder',
    'Right-hand bat',
    'Right-arm offbreak',
    'Australia'
);

-- 5. Insert demo player match statistics
-- Look up the real fixture_id instead of assuming it is 990001.
INSERT OR IGNORE INTO player_match_stats (
    stat_id, player_id, fixture_id, format,
    runs, balls_faced, fours, sixes, wickets,
    overs_bowled, runs_conceded, catches
)
VALUES
(
    990001,
    990001,
    (SELECT fixture_id FROM fixtures
     WHERE match_id = 990001
       AND date = '2099-01-10'
       AND match = 'Demo Match 1'),
    'ODI',
    75, 60, 8, 2, 0, 0, 0, 1
),
(
    990002,
    990002,
    (SELECT fixture_id FROM fixtures
     WHERE match_id = 990001
       AND date = '2099-01-10'
       AND match = 'Demo Match 1'),
    'ODI',
    32, 25, 3, 1, 2, 6.0, 30, 0
);

COMMIT;
