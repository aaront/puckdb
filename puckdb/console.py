import click

from . import db


@click.command(help='Initialize the database')
@click.argument('connect', nargs=1, required=False)
def init(connect=None):
    if not db.connect_str:
        if not connect:
            raise Exception('Must provide a connection string')
    db.create(connect)


@click.group()
@click.version_option()
def main():
    pass


main.add_command(init)

if __name__ == '__main__':
    main()
