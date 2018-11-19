TEAM_ID=1460893 #Go to "my team", click "view gameweek history", look at url. Taken from https://www.reddit.com/r/FantasyPL/comments/4tki9s/fpl_id/
PLAYERS_URL="https://fantasy.premierleague.com/drf/bootstrap-static"
TEAMS_URL="https://fantasy.premierleague.com/drf/teams"
GAMES_URL="https://fantasy.premierleague.com/drf/element-summary/"
ELEMENT_TYPE_TO_POSITION={1:'GKP',2:'DEF',3:'MID',4:'FWD'}
POSITION_TO_NUMBER={'GKP':1,'DEF':4,'MID':4,'FWD':2}
THRESH=0.8 #if player has played less than this many proportion of games, he will probably not play the next game (arbitrary)