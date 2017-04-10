import sys

from datetime import datetime

import click
import click_datetime

from puckdb import db, fetcher

DATE_PARAM = click_datetime.Datetime(format='%Y-%m-%d')


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.command(help='Initialize the database')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to init the database?')
def init():
    db.create()
    fetcher.get_teams()


@click.command(help='Remove all data from the database')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the database?')
def drop():
    db.drop()


@click.command()
@click.option('--from-date', type=DATE_PARAM, default=datetime(2016, 10, 1))
@click.option('--to-date', type=DATE_PARAM, default=datetime.now())
def fetch(from_date, to_date):
    fetcher.get_games(from_date, to_date)


@click.group()
@click.version_option()
def main():
    if db.connect_str is None:
        click.echo('ERROR: `PUCKDB_DATABASE` environment variable not specified.')
        sys.exit(1)

main.add_command(get)
main.add_command(init)
main.add_command(drop)

if __name__ == '__main__':
    main()
