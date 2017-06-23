import ast
import re

from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('puckdb/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='puckdb',
    author='Aaron Toth',
    version=version,
    url='https://github.com/aaront/puckdb',
    description='An async-first hockey data extractor and API',
    long_description=open('README.rst').read(),
    test_suite="tests",
    include_package_data=True,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    package_dir={'puckdb': 'puckdb'},
    license='Apache 2.0',
    install_requires=[
        'aiohttp',
        'asyncpgsa',
        'click',
        'click-datetime',
        'python-dateutil',
        'pytz',
        'psycopg2',
        'sqlalchemy',
        'ujson',
        'marshmallow',
        'marshmallow-enum',
        'python-dotenv'
    ],
    entry_points='''
        [console_scripts]
        puckdb=puckdb.console:main
    ''',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries'
    )
)
