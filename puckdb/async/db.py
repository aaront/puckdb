from contextlib import contextmanager

from aiopg.sa import create_engine

from .. import conf


@contextmanager
async def get_engine():
    async with create_engine(dsn=conf.get_db()) as engine:
        await engine


__all__ = ['get_engine']
