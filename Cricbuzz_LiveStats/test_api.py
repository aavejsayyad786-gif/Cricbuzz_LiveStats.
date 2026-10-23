
from api.cricbuzz_api import get_teams

try:
    teams = get_teams()
    print(f"Success! Received {len(teams)} team records.")

    for team in teams[:5]:
        print(team)

except Exception as exc:
    print(f"API test failed: {exc}")
