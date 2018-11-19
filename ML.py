from constants import *
import pandas as pd
from API import get_current_gameweek

def make_training_sets(games_df):
    gameweek = get_current_gameweek(GAMES_URL)
    IDs = games_df['id']
    data_to_add_back=games_df[['id','opponent_team_'+str(gameweek-1),'was_home_'+str(gameweek-1)]]
    X = games_df[games_df.columns.drop(list(games_df.filter(regex='_'+str(gameweek-1))))]
    X = X.merge(data_to_add_back, on='id')
    X = X.drop('id',axis=1)
    X_tot = X
    X = X.loc[X.filter(regex='total_points').sum(axis=1)!=0,] #remove players who never scored points
    y = games_df['total_points_'+str(gameweek-1)]
    y = y.loc[X_tot.filter(regex='total_points').sum(axis=1)!=0]
    return(X,y)