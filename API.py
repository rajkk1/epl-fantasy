from constants import *
from utils import *
import pandas as pd
import requests

def create_team_stats(teams_URL):
    """
    Creates a table of all the teams in the Premier League with many of their attributes (according to the fantasy epl website)
   
    :param str teams_URL: hyperlink to the teams json file
    :returns: pandas dataframe with team info 
    """
    team_stats = pd.read_json(teams_URL)
    columns=['id','name','strength','position','form','played',
             'strength_attack_away','strength_attack_home',
             'strength_defence_away','strength_defence_home',
             'strength_overall_away','strength_overall_home']
    team_stats=team_stats[columns]
    team_stats.rename(columns={'id':'team', 'form':'team_form'}, inplace=True)
    team_stats['team'] = team_stats['team'].astype(str)    
    return(team_stats)

def create_player_summary(players_URL,team_stats):
    """
    Creates a pandas dataframe of current player stats. Note that all stats are normalized by total games played except for total points
   
    :param str players_URL: hyperlink to the player summary json file
    :param pandas.DataFrame team_stats: dataframe of team statistics
    :returns: pd.DataFrame with player info 
    """
    r = requests.get(players_URL)
    json_players_summary = r.json()
    player_summary=pd.DataFrame.from_dict(json_players_summary['elements'])
    player_summary["team"] = player_summary["team"].astype(str)
    player_summary=player_summary.merge(team_stats[['team','played']], left_on='team', right_on='team', how='inner')
    player_summary['points_per_game'] = pd.to_numeric(player_summary['points_per_game'], errors='coerce') #to change points_per_game from string to float
    cols_to_normalize = ['assists','bonus','bps','clean_sheets','own_goals',
                         'dreamteam_count','goals_conceded','goals_scored',
                         'minutes','penalties_missed','penalties_saved','red_cards',
                         'saves','yellow_cards']
    for col in cols_to_normalize:
        player_summary[col] = player_summary[col]/player_summary['played']
        player_summary.rename(columns={col:col+"_avg"}, inplace=True)
    cols_normalized = [s + "_avg" for s in cols_to_normalize]
    player_summary['chance_of_playing_next_round'] = player_summary['chance_of_playing_next_round']/100
    player_summary["chance_of_playing_next_round"] = player_summary["chance_of_playing_next_round"].fillna(1)
    other_cols=['chance_of_playing_next_round','creativity', 'ea_index',
                'element_type', 'ep_next', 'ep_this', 'event_points', 'first_name',
                'form', 'ict_index', 'id','influence', 'now_cost',
                'points_per_game','second_name', 'selected_by_percent', 'special',
                'squad_number', 'status', 'team', 'team_code', 'threat', 'total_points',
                'value_form', 'value_season', 'web_name']
    columns = cols_normalized + other_cols
    player_summary = player_summary[columns]
    player_summary['field_position'] = player_summary['element_type'].apply(lambda x: ELEMENT_TYPE_TO_POSITION[x])
    return(player_summary)

def create_games_data(games_URL,player_summary):
    """
    Creates a pandas dataframe of game performances for every player with player id number
   
    :param str gamesURL: hyperlink to the games summary json file
    :param int numPlayers: total number of players in Premier League
    :returns: pd.DataFrame with player performance for each game the player has played 
    """
    num_players=len(player_summary)
    player_info=player_summary[['id','team', 'field_position']]
    cols=['assists','attempted_passes', 'big_chances_created', 'big_chances_missed',
          'bonus', 'bps', 'clean_sheets', 'clearances_blocks_interceptions',
          'completed_passes', 'creativity', 'dribbles', 'errors_leading_to_goal',
          'errors_leading_to_goal_attempt', 'fouls', 'goals_conceded', 'goals_scored',
          'influence', 'key_passes', 'minutes', 'offside', 'open_play_crosses',
          'opponent_team', 'own_goals', 'penalties_conceded', 'penalties_missed',
          'penalties_saved', 'recoveries', 'red_cards', 'round', 'saves', 'selected',
          'tackled', 'tackles', 'target_missed', 'threat', 'total_points', 'transfers_balance',
          'transfers_in', 'transfers_out', 'value', 'was_home', 'winning_goals', 'yellow_cards']
    games_data=[]
    for i in log_progress(range(1,num_players+1)):
        r = requests.get(games_URL+str(i))
        jsonResponse = r.json()
        curr_games_rows = pd.DataFrame.from_dict(jsonResponse['history'])
        curr_games_rows['creativity'] = curr_games_rows['creativity'].astype(float)
        curr_games_rows['influence'] = curr_games_rows['influence'].astype(float)
        curr_games_rows['threat'] = curr_games_rows['threat'].astype(float)
        id_col = curr_games_rows[0:1]['id']
        rows=[id_col]
        for j in range(len(curr_games_rows)):
            row = curr_games_rows[j:j+1]
            row = row[cols]
            row.columns = [str(col) + '_' + str(j+1) for col in row.columns]
            row.reset_index(drop=True, inplace=True) #to avoid NaNs when concatinating https://stackoverflow.com/questions/40339886/pandas-concat-generates-nan-values
            rows.append(row)
        curr_games_df = pd.concat(rows, axis=1)
        games_data.append(curr_games_df)
    games_df=pd.concat(games_data, axis=0)
    games_df=games_df.merge(player_info, on='id')
    games_df=games_df.dropna()
    regex_cols_to_str=['team']
    cols_to_str=[]
    for col in regex_cols_to_str:
        cols_to_str = cols_to_str+(list(games_df.filter(regex=col)))
    for col in cols_to_str:
        games_df[col] = games_df[col].astype(int)
        games_df[col] = games_df[col].astype(str)
    games_df["was_home_1"]=games_df["was_home_1"].astype(object)
    return(games_df)

def get_current_gameweek(games_URL):
    r = requests.get(games_URL+str(1))
    json_response = r.json()
    gameweek=json_response['fixtures'][0]['event']
    return(gameweek)

def my_current_team(games_URL, player_summary):
    gameweek_ind=get_current_gameweek(GAMES_URL)-1
    my_team_roster_URL="https://fantasy.premierleague.com/drf/entry/%d/event/%d/picks" % (TEAM_ID,gameweek_ind)
    r = requests.get(my_team_roster_URL)
    json_response_team = r.json()
    current_team = pd.DataFrame.from_dict(json_response_team['picks'])
    current_team.rename(columns={'element':'id'}, inplace=True)
    current_team = current_team.merge(player_summary, on='id')
    return(current_team)

def find_maxed_out_team(my_team, team_stats):
    maxed_out_teams=[]
    for team in set(my_team['team']):
        if sum(my_team['team']==team) > 2:
            team_name = team_stats.loc[team_stats['team']==team,'name'].as_matrix()[0]
            maxed_out_teams.append(team_name)
    return(maxed_out_teams)