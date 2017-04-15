import asyncio

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

__title__ = 'puckdb'
__author__ = 'Aaron Toth'
__version__ = '0.0.1'
