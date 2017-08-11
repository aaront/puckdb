import re
from datetime import datetime

import pytz

from . import model

iso_date_format = '%Y-%m-%dT%H:%M:%SZ'


def team(team_json: dict) -> dict:
    return dict(
        id=int(team_json['id']),
        name=team_json['name'],
        team_name=team_json['teamName'],
        abbreviation=team_json['abbreviation'],
        city=team_json['locationName']
    )


def player(player_json: dict) -> dict:
    pos = player_json['primaryPosition']['name'].replace(' ', '_').lower()
    return dict(
        id=int(player_json['id']),
        first_name=player_json['firstName'],
        last_name=player_json['lastName'],
        position=model.parse_enum(model.PlayerPosition, pos).name
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
        date_start=_parse_iso_date(game_datetime['dateTime'])
    )
    if 'endDateTime' in game_datetime:
        data['date_end'] = _parse_iso_date(game_datetime['endDateTime'])
    return data


def event(game_id: int, event_json: dict):
    if 'team' not in event_json:
        return None
    about = event_json['about']
    result = event_json['result']
    event_type = model.parse_enum(model.EventType, result['eventTypeId'])
    if event_type is None:
        return None
    ev_data = dict(
        game=game_id,
        id=about['eventId'],
        team=event_json['team']['id'],
        type=event_type.name,
        date=_parse_iso_date(about['dateTime']),
        period=about['period']
    )
    if event_type is model.EventType.shot and 'secondaryType' in result:
        ev_data['shot_type'] = _parse_shot_type(result['secondaryType']).name
    return ev_data


shot_sep = re.compile(r'(\w+)[\s|-]*')


def _parse_shot_type(shot_type: str) -> model.ShotType:
    shot = shot_sep.match(shot_type).group(1).lower()
    try:
        return model.parse_enum(model.ShotType, shot)
    except ValueError:
        if shot == 'wrap':
            return model.ShotType.wrap_around
    raise ValueError('\'{}\' is not parseable'.format(shot_type))


def _parse_iso_date(date_str: str) -> datetime:
    return pytz.utc.localize(datetime.strptime(date_str, iso_date_format))
