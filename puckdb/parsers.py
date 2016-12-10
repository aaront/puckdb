from datetime import datetime, timedelta

from . import db


def team(tm: dict):
    return dict(
        id=tm['id'],
        name=tm['name'],
        team_name=tm['teamName'],
        abbreviation=tm['abbreviation'],
        city=tm['locationName']
    )


def player(pl: dict):
    return dict(
        id=pl['id'],
        first_name=pl['firstName'],
        last_name=pl['lastName'],
        position=pl['primaryPosition']['name'].replace(' ', '_').lower()
    )


def event(ev: dict):
    ev['id'] = event['eventId']
    ev.update(event['coordinates'])
    about = event['about']
    period = int(about['period'])
    ev['period'] = period
    period_time = datetime.strptime(about['periodTime'], '%M:%S')
    period_time = timedelta(minutes=period_time.minute, seconds=period_time.second)
    ev['periodTime'] = period_time
    ev['time'] = ((period - 1) * timedelta(minutes=20)) + period_time
    result = event['result']
    result['type'] = db.Event.parse_type(result['eventTypeId'])
    if 'strength' in result:
        result['strength'] = result['strength']['code']
    del result['event']
    del result['eventCode']
    del result['eventTypeId']
    ev.update(result)
    if 'team' in event:
        ev['team_id'] = int(event['team']['id'])
    return ev
