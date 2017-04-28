import pytz
from dateutil import parser

from . import model


def team(team_json: dict) -> model.Team:
    return model.Team(
        id=int(team_json['id']),
        name=team_json['name'],
        team_name=team_json['teamName'],
        abbreviation=team_json['abbreviation'],
        city=team_json['locationName']
    )


def player(player_json: dict) -> model.Player:
    pos = player_json['primaryPosition']['name'].replace(' ', '_').lower()
    return model.Player(
        id=int(player_json['id']),
        first_name=player_json['firstName'],
        last_name=player_json['lastName'],
        position=model.parse_enum(model.PlayerPosition, pos)
    )


def game(game_json: dict):
    game_data = game_json['gameData']
    game_datetime = game_data['datetime']
    for type, team in game_data['teams'].items():
        if type == 'home':
            home_team = team
        else:
            away_team = team
    data = dict(
        id=int(game_json['gamePk']),
        away=int(away_team['id']),
        home=int(home_team['id']),
        date_start=parser.parse(game_datetime['dateTime']).astimezone(pytz.utc)
    )
    if 'endDateTime' in game_datetime:
        data['date_end'] = parser.parse(game_datetime['endDateTime']).astimezone(pytz.utc)
    return data


def event(game_id: int, event_json: dict):
    if 'team' not in event_json:
        return None
    about = event_json['about']
    result = event_json['result']
    event_type = model.parse_enum(model.EventType, 'eventTypeId')
    if event_type is None:
        return None
    ev_data = dict(
        game=game_id,
        id=about['eventId'],
        team=event_json['team']['id'],
        type=event_type.name,
        date=parser.parse(about['dateTime']).astimezone(pytz.utc),
        period=about['period']
    )
    # if event_type is db.EventType.shot and 'secondaryType' in result:
    #     ev_data['shot_type'] = db.Event.parse_shot_type(result['secondaryType']).value
    return ev_data
