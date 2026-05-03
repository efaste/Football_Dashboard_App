import streamlit as st
import requests
import pandas as pd

# Define European leagues with their API search names
leagues = {
    "English Premier League": "English_Premier_League",
    "Spanish La Liga": "Spanish La Liga",
    "German Bundesliga": "German Bundesliga",
    "Italian Serie A": "Italian Serie A",
    "French Ligue 1": "French Ligue 1"
}

@st.cache_data
def get_players(league_name):
    """Fetch all players from the selected league."""
    try:
        # Get teams in the league
        teams_url = f"https://www.thesportsdb.com/api/v1/json/123/search_all_teams.php?l={league_name}"
        teams_response = requests.get(teams_url)
        teams_data = teams_response.json()
        
        if 'teams' not in teams_data or not teams_data['teams']:
            st.error(f"No teams found for {league_name}")
            return pd.DataFrame()
        
        teams = teams_data['teams']
        all_players = []
        
        # For each team, get players
        for team in teams:
            team_id = team['idTeam']
            team_name = team['strTeam']
            players_url = f"https://www.thesportsdb.com/api/v1/json/123/lookup_all_players.php?id={team_id}"
            players_response = requests.get(players_url)
            players_data = players_response.json()
            
            if 'player' in players_data and players_data['player']:
                for player in players_data['player']:
                    player['team'] = team_name
                    all_players.append(player)
        
        if not all_players:
            st.warning(f"No players found for {league_name}")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_players)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

# Streamlit app
st.title("European Soccer Players Dashboard")

st.markdown("Select a European league to view all players across teams in that league.")

selected_league = st.selectbox("Choose a League", list(leagues.keys()))

if selected_league:
    league_api_name = leagues[selected_league]
    
    with st.spinner(f"Fetching players from {selected_league}..."):
        df = get_players(league_api_name)
    
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
st.markdown("Data sourced from TheSportsDB API. Note: Free API has rate limits.")