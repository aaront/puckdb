import click

from . import conf, db


@click.command(help='Initialize the database')
@click.argument('connect', nargs=1, required=False)
def init(connect=None):
    if not conf.get_db():
        if not connect:
            raise Exception('Must provide a connection string')
        conf.init(connect)
    db.create()


@click.group()
@click.version_option()
def main():
    pass


main.add_command(init)

if __name__ == '__main__':
    main()
