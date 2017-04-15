import asyncio
import sys
from datetime import datetime

import click
import click_datetime

from puckdb import db, fetch

DATE_PARAM = click_datetime.Datetime(format='%Y-%m-%d')


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def _setup():
    loop.run_until_complete(db.setup(loop=loop))


@click.command(help='Initialize the database')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to init the database?')
def init():
    db.create()
    loop.run_until_complete(fetch.get_teams(loop=loop))


@click.command(help='Remove all data from the database')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the database?')
def drop():
    db.drop()


@click.command()
@click.option('--from-date', type=DATE_PARAM, default=datetime(2016, 10, 1))
@click.option('--to-date', type=DATE_PARAM, default=datetime.now())
def get(from_date, to_date):
    games = loop.run_until_complete(fetch.get_games(from_date=from_date, to_date=to_date, loop=loop))
    click.echo(len(games))


@click.group()
@click.version_option()
def main():
    if db.connect_str is None:
        click.echo('ERROR: `PUCKDB_DATABASE` environment variable not specified.')
        sys.exit(1)
    _setup()


main.add_command(get)
main.add_command(init)
main.add_command(drop)

loop = asyncio.get_event_loop()

if __name__ == '__main__':
    main()
