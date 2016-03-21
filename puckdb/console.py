import click


@click.command()
def init():
    pass


@click.group
@click.version_option()
def main():
    pass

main.add_command(init)

if __name__ == '__main__':
    main()
