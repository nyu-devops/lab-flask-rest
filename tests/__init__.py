"""
Shared test configuration

The tests run against their own Redis database number so that
Counter.remove_all() (FLUSHDB) never wipes data a developer keeps in the
default database. Set TEST_DATABASE_URI to override this entirely.
"""
import os
from urllib.parse import urlsplit, urlunsplit
from service.config import DATABASE_URI

TEST_DATABASE_NUMBER = 15


def _with_database_number(uri: str, number: int) -> str:
    """Returns the Redis uri with its database number replaced"""
    parts = urlsplit(uri)
    return urlunsplit(parts._replace(path=f"/{number}"))


TEST_DATABASE_URI = os.getenv("TEST_DATABASE_URI") or _with_database_number(
    DATABASE_URI, TEST_DATABASE_NUMBER
)
