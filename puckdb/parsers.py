import pytz
from dateutil import parser

from . import model


def team(tm: dict):
    return dict(
        id=int(tm['id']),
        name=tm['name'],
        team_name=tm['teamName'],
        abbreviation=tm['abbreviation'],
        city=tm['locationName']
    )


def player(pl: dict):
    return dict(
        id=int(pl['id']),
        first_name=pl['firstName'],
        last_name=pl['lastName'],
        position=pl['primaryPosition']['name'].replace(' ', '_').lower()
    )


def game(gm: dict):
    game_data = gm['gameData']
    game_datetime = game_data['datetime']
    for type, team in game_data['teams'].items():
        if type == 'home':
            home_team = team
        else:
            away_team = team
    data = dict(
        id=int(gm['gamePk']),
        away=int(away_team['id']),
        home=int(home_team['id']),
        date_start=parser.parse(game_datetime['dateTime']).astimezone(pytz.utc)
    )
    if 'endDateTime' in game_datetime:
        data['date_end'] = parser.parse(game_datetime['endDateTime']).astimezone(pytz.utc)
    return data


def event(gid: int, ev: dict):
    if 'team' not in ev:
        return None
    about = ev['about']
    result = ev['result']
    event_type = model.parse_enum(model.EventType, 'eventTypeId')
    if event_type is None:
        return None
    ev_data = dict(
        game=gid,
        id=about['eventId'],
        team=ev['team']['id'],
        type=event_type.name,
        date=parser.parse(about['dateTime']).astimezone(pytz.utc),
        period=about['period']
    )
    # if event_type is db.EventType.shot and 'secondaryType' in result:
    #     ev_data['shot_type'] = db.Event.parse_shot_type(result['secondaryType']).value
    return ev_data
