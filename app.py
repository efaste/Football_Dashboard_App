import streamlit as st
import requests
import pandas as pd

# ESPN league IDs for the supported leagues.
leagues = {
    "English Premier League": "eng.1",
    "Spanish La Liga": "esp.1",
    "German Bundesliga": "ger.1",
    "Italian Serie A": "ita.1",
    "French Ligue 1": "fra.1",
}

ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


@st.cache_data(ttl=3600)
def get_players(league_id):
    """Fetch and normalize the selected league's ESPN team rosters."""
    try:
        teams_url = f"{ESPN_API_BASE}/{league_id}/teams"
        teams_data = _get_api_json(teams_url, params={"limit": 100})
        leagues_data = teams_data.get("sports", [{}])[0].get("leagues", [])
        teams = leagues_data[0].get("teams", []) if leagues_data else []
        if not teams:
            raise ValueError(f"ESPN returned no teams for league {league_id}.")

        players = []
        for entry in teams:
            team = entry.get("team", {})
            team_id = team.get("id")
            team_name = team.get("displayName") or team.get("name")
            if not team_id or not team_name:
                continue

            roster_url = f"{ESPN_API_BASE}/{league_id}/teams/{team_id}/roster"
            roster_data = _get_api_json(roster_url)
            for athlete in roster_data.get("athletes", []):
                position = athlete.get("position") or {}
                birth_place = athlete.get("birthPlace") or {}
                players.append(
                    {
                        "strPlayer": athlete.get("displayName") or athlete.get("fullName", ""),
                        "strPosition": position.get("displayName") or position.get("name", ""),
                        "strNationality": athlete.get("citizenship")
                        or athlete.get("citizenshipCountry", ""),
                        "team": team_name,
                        "dateBorn": (athlete.get("dateOfBirth") or "")[:10],
                        "strBirthLocation": ", ".join(
                            filter(
                                None,
                                (
                                    birth_place.get("city"),
                                    birth_place.get("state"),
                                    birth_place.get("country"),
                                ),
                            )
                        ),
                    }
                )

        if not players:
            raise ValueError(f"ESPN returned no player rosters for league {league_id}.")
        return pd.DataFrame(players)
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching player data from ESPN: {e}")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"Invalid response from ESPN: {e}")
        return pd.DataFrame()


def _get_api_json(url, params=None):
    response = requests.get(url, params=params, timeout=15)

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        wait_message = (
            f" Try again in {retry_after} seconds."
            if retry_after
            else " Try again later."
        )
        raise requests.exceptions.HTTPError(
            f"ESPN rate limit reached (HTTP 429).{wait_message}",
            response=response,
        )

    response.raise_for_status()
    try:
        return response.json()
    except ValueError as e:
        content_type = response.headers.get("Content-Type", "unknown")
        raise ValueError(
            f"ESPN returned a non-JSON response "
            f"(HTTP {response.status_code}, content type {content_type})."
        ) from e

# Streamlit app
st.title("European Soccer Players Dashboard")

st.markdown("Select a European league to view all players across teams in that league.")

selected_league = st.selectbox("Choose a League", list(leagues.keys()))

if selected_league:
    league_id = leagues[selected_league]
    
    with st.spinner(f"Fetching players from {selected_league}..."):
        df = get_players(league_id)
    
    if not df.empty:
        st.subheader(f"Players in {selected_league}")
        
        # Display some stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Players", len(df))
        with col2:
            st.metric("Unique Nationalities", df['strNationality'].nunique())
        with col3:
            st.metric("Teams", df['team'].nunique())
        
        # Filters
        st.subheader("Filters")
        col1, col2 = st.columns(2)
        with col1:
            positions = df['strPosition'].dropna().unique()
            selected_position = st.multiselect("Filter by Position", positions, default=positions)
        with col2:
            nationalities = df['strNationality'].dropna().unique()
            selected_nationality = st.multiselect("Filter by Nationality", nationalities, default=nationalities)
        
        # Apply filters
        filtered_df = df[
            (df['strPosition'].isin(selected_position)) &
            (df['strNationality'].isin(selected_nationality))
        ]
        
        # Display table
        st.dataframe(
            filtered_df[['strPlayer', 'strPosition', 'strNationality', 'team', 'dateBorn', 'strBirthLocation']],
            use_container_width=True
        )
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"{selected_league.replace(' ', '_')}_players.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available for the selected league.")

st.markdown("---")
st.markdown("Player data sourced from ESPN.")