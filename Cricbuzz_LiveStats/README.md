# 🏏 Cricbuzz LiveStats

**Real-Time Cricket Insights & SQL-Based Analytics**

Cricbuzz LiveStats is a Python-based cricket dashboard built with Streamlit. It integrates cricket data from a Cricbuzz API provider through RapidAPI and provides database management and SQL analytics features.

## Features

- **Home Dashboard:** Project overview and navigation.
- **Teams:** Fetch and explore cricket team information.
- **Live Matches:** View available live-match data from the API.
- **Fixtures:** Browse cricket schedules and fixture information.
- **Player Directory:** Explore available player information.
- **Top Player Stats:** View player analytics and batting/bowling rankings based on available data.
- **CRUD Operations:** Create, read, update, and delete player and player-stat records.
- **SQL Analytics:** Run predefined SQL questions and explore database results.
- **SQLite Database:** Store and manage cricket-related records.
- **SQL Scripts:** Reproducible database schema and demo sample data.

*Live data availability depends on the API provider, endpoint configuration, and subscription limits. Some player rankings are calculated from locally stored match statistics rather than official live API rankings.*

## Technology Stack

- Python
- Streamlit
- SQLite
- SQL
- Pandas
- Plotly
- Requests
- RapidAPI cricket data provider
- python-dotenv

## Project Structure

```text
Cricbuzz_LiveStats/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── api/
│   └── cricbuzz_api.py
├── database/
│   ├── cricbuzz.db
│   ├── db_manager.py
│   └── crud_manager.py
├── services/
│   ├── sql_queries.py
│   └── player_analytics.py
└── sql/
    ├── schema.sql
    └── sample_data.sql
```

Additional files and modules may be present in the project.

## Prerequisites

- Python installed on Windows
- VS Code or another Python editor
- A RapidAPI account and valid API key for the configured cricket API

## Setup on Windows

1. Open the `Cricbuzz_LiveStats` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment if you do not already have one:

   ```powershell
   python -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env` and configure the environment variables required by `api/cricbuzz_api.py`. Add your own valid RapidAPI key and the correct API host and endpoint settings.

7. Start the application:

   ```powershell
   python -m streamlit run app.py
   ```

8. Open the local URL printed in the terminal by Streamlit.

## Environment Configuration

Keep API credentials in `.env`, not in source code.

Example:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=your_configured_api_host
DATABASE_URL=sqlite:///database/cricbuzz.db
```

Use the exact variable names expected by your API module and application configuration. The example values above are placeholders.

**Never commit or share your real `.env` file or API key.**

## Database Setup

The SQLite database is located at:

```text
database/cricbuzz.db
```

The SQL scripts are:

- `sql/schema.sql` — defines the database tables and indexes.
- `sql/sample_data.sql` — inserts demo records for testing.

To validate the scripts from the project root, run the project's SQL validation test if available. The schema and sample-data scripts have been tested successfully using an in-memory SQLite database.

## SQL Analytics

The application provides predefined SQL questions for analyzing stored cricket and player statistics. Queries can cover filtering, aggregation, joins, rankings, and other analytical operations supported by the implemented questions.

Results depend on the records available in the local database.

## Testing

Before submitting the project:

1. Start the Streamlit application.
2. Open each dashboard page.
3. Verify the API-backed pages with the configured API.
4. Test CRUD operations using demo records.
5. Execute SQL analytics questions.
6. Validate `sql/schema.sql` and `sql/sample_data.sql`.
7. Confirm that the README and dependency list match the actual project.

## Security Notes

- Do not include `.env` or real API keys in the submission.
- Keep `.venv` and Python cache folders out of the submission ZIP.
- Use demo records when testing destructive CRUD operations.

## Limitations

- Live match data may be empty when no matches are live or when the API provider returns no records.
- API access depends on the provider's availability and subscription limits.
- Local analytics reflect the data stored in the database and should not be treated as official rankings unless verified against the provider.

## Project Title

**Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics**

