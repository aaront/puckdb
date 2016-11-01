from datetime import datetime, timedelta

from .. import filters, scrapers, models


def get_events(game: dict):
    games = scrapers.GameScraper(filter).get()
    for game in games:
        for event in game['liveData']['plays']['allPlays']:
            ev = dict(game_id=game['gameData']['game']['pk'])
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
            result['type'] = models.Event.parse_type(result['eventTypeId'])
            if 'strength' in result:
                result['strength'] = result['strength']['code']
            del result['event']
            del result['eventCode']
            del result['eventTypeId']
            ev.update(result)
            if 'team' in event:
                ev['team_id'] = int(event['team']['id'])
            yield ev