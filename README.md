# European Soccer Players Dashboard

A Streamlit dashboard to explore soccer players across major European leagues.

## Features

- Select from major European leagues: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- View all players with details like position, nationality, team, birth date, and location
- Filter by position and nationality
- Download filtered data as CSV
- Basic statistics: total players, unique nationalities, number of teams

## Installation

1. Clone or download this repository.
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

Open the provided URL in your browser to interact with the dashboard.

## Data Source

Data is fetched from TheSportsDB API (free tier). The API has a rate limit of 30 requests per minute.

## Troubleshooting

- **No data displayed**: Check your internet connection. The API might be down or rate-limited.
- **Slow loading**: Fetching data for a full league (20+ teams) requires multiple API calls.
- **Errors**: Ensure all dependencies are installed. If API key issues (though free tier doesn't require one), contact TheSportsDB.

## Requirements

- Python 3.7+
- streamlit
- requests
- pandas