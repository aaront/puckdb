import asyncio

from puckdb import server

loop = asyncio.get_event_loop()


def main():
    server.run(loop)


if __name__ == '__main__':
    main()
