
"""Cricbuzz LiveStats API client."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load .env from the project root.
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}"

API_KEY = os.getenv("RAPIDAPI_KEY", "").strip()

LIVE_MATCHES_ENDPOINT = os.getenv(
    "LIVE_MATCHES_ENDPOINT", "/cricket-livescores"
).strip()

FIXTURES_ENDPOINT = os.getenv(
    "FIXTURES_ENDPOINT", "/cricket-schedule"
).strip()

SERIES_ENDPOINT = os.getenv(
    "SERIES_ENDPOINT", "/cricket-series-international"
).strip()

TEAMS_ENDPOINT = "/cricket-teams"

# Set this only after copying the exact path from RapidAPI.
PLAYERS_ENDPOINT = os.getenv("PLAYERS_ENDPOINT", "").strip()


class CricbuzzAPIError(Exception):
    """Raised when the Cricbuzz API request fails."""


def _request(endpoint, params=None):
    """Send a GET request to the configured RapidAPI host."""
    if not API_KEY:
        raise CricbuzzAPIError(
            "RAPIDAPI_KEY is missing. Check your project's .env file."
        )

    if not endpoint or not endpoint.startswith("/"):
        raise CricbuzzAPIError(
            "The API endpoint must be a verified path beginning with '/'."
        )

    url = f"{BASE_URL}{endpoint}"

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST,
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()

    except requests.Timeout as exc:
        raise CricbuzzAPIError(
            "The Cricbuzz API request timed out. Please try again."
        ) from exc

    except requests.RequestException as exc:
        status = getattr(
            getattr(exc, "response", None), "status_code", None
        )

        if status == 401 or status == 403:
            message = (
                "RapidAPI rejected the request. Check your API key, "
                "subscription, and endpoint permissions."
            )
        elif status == 429:
            message = (
                "RapidAPI rate limit or quota reached. "
                "Check your plan's usage limits."
            )
        else:
            message = f"Cricbuzz API request failed: {exc}"

        raise CricbuzzAPIError(message) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise CricbuzzAPIError(
            "The API returned a response that is not valid JSON."
        ) from exc

    if isinstance(data, dict):
        if data.get("status") == "failure":
            raise CricbuzzAPIError(
                str(data.get("message", "The API reported a failure."))
            )

    return data


def _extract_records(data):
    """Extract a list of records from common API response formats."""
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    response_data = data.get("response")

    if isinstance(response_data, list):
        return response_data

    if isinstance(response_data, dict):
        for key in ("items", "data", "matches", "series", "teams", "players"):
            value = response_data.get(key)
            if isinstance(value, list):
                return value

    for key in ("data", "items", "matches", "series", "teams", "players"):
        value = data.get(key)
        if isinstance(value, list):
            return value

    return []


def _flatten_fixtures(data):
    """Flatten the nested Cricbuzz schedule response into individual matches."""
    fixtures = []

    # Handle the API's top-level response structure.
    response = data.get("response", data) if isinstance(data, dict) else data

    if isinstance(response, dict):
        schedules = response.get("schedules", [])
    elif isinstance(response, list):
        schedules = response
    else:
        return fixtures

    for schedule in schedules:
        if not isinstance(schedule, dict):
            continue

        # Each schedule may contain a scheduleAdWrapper.
        wrapper = schedule.get("scheduleAdWrapper", schedule)

        if not isinstance(wrapper, dict):
            continue

        match_schedule_list = wrapper.get("matchScheduleList", [])

        for series in match_schedule_list:
            if not isinstance(series, dict):
                continue

            series_name = series.get("seriesName", "")
            matches = series.get("matchInfo", [])

            # Normally matchInfo is a list, but handle a single match too.
            if isinstance(matches, dict):
                matches = [matches]

            for match in matches:
                if not isinstance(match, dict):
                    continue

                team1 = match.get("team1") or {}
                team2 = match.get("team2") or {}
                venue = match.get("venueInfo") or {}

                # Preserve original fields and add convenient display fields.
                fixture = dict(match)
                fixture["seriesName"] = (
                    match.get("seriesName") or series_name
                )
                fixture["team1Name"] = team1.get("teamName", "")
                fixture["team2Name"] = team2.get("teamName", "")
                fixture["venue"] = venue.get("ground", "")
                fixture["city"] = venue.get("city", "")
                fixture["country"] = venue.get("country", "")
                fixtures.append(fixture)

    return fixtures

def get_teams():
    """Get the list of cricket teams."""
    data = _request(TEAMS_ENDPOINT)
    return _extract_records(data)


def get_raw_live_matches():
    """Get the unmodified live-match API response."""
    return _request(LIVE_MATCHES_ENDPOINT)


def get_live_matches():
    """Get live-match records from the API."""
    data = get_raw_live_matches()
    return _extract_records(data)


def get_fixtures():
    """Get scheduled fixtures from the API."""
    data = _request(FIXTURES_ENDPOINT)
    return _flatten_fixtures(data)


def get_series():
    """Get cricket series from the API."""
    data = _request(SERIES_ENDPOINT)
    return _extract_records(data)


def get_players_list(team_id=2):
    """Fetch players for a team from the Cricbuzz API."""
    if not PLAYERS_ENDPOINT:
        raise CricbuzzAPIError(
            "Set PLAYERS_ENDPOINT in your .env file."
        )

    data = _request(
        PLAYERS_ENDPOINT,
        params={"teamid": team_id},
    )

    records = _extract_records(data)
    players = []

    for player in records:
        if not isinstance(player, dict):
            continue

        players.append({
            "id": player.get("id"),
            "slug": player.get("slug", ""),
            "name": player.get("title", "Unknown player"),
            "image": player.get("image", ""),
        })

    return players