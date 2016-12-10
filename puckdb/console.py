import click

from puckdb import db


@click.command(help='Initialize the database')
@click.argument('connect', nargs=1, required=False)
def init(connect=None):
    if not db.connect_str:
        if not connect:
            raise Exception('Must provide a connection string')
    db.create(connect)


@click.group()
def fetch():
    pass


@click.group()
@click.version_option()
def main():
    pass


fetch.add_command(teams)
main.add_command(fetch)
main.add_command(init)

if __name__ == '__main__':
    main()
