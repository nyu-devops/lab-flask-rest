######################################################################
# Copyright 2016, 2020 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Counter Model
"""
import logging
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)


class DatabaseConnectionError(RedisConnectionError):
    """Generic Exception for Redis database connection errors"""


class Counter:
    """An integer counter that is persisted in Redis

    Call Counter.connect() with a Redis URI before use. The application
    takes the URI from service.config.DATABASE_URI, which has the form:

        redis://userid:password@localhost:6379/0

    This follows the same standards as SQLAlchemy URIs
    """

    redis = None

    def __init__(self, name: str = "hits", *, create: bool = True):
        """Constructor

        Arguments:
            name: the name of the counter
            create: when True (the default) the counter is created in Redis
                with a value of 0 if it does not already exist. An existing
                counter is never overwritten. Pass create=False to wrap a
                counter that is already known to exist without touching Redis.
        """
        self.name = name
        if create:
            Counter.redis.set(self.name, 0, nx=True)

    @property
    def value(self):
        """Returns the current value of the counter"""
        return int(Counter.redis.get(self.name))

    @value.setter
    def value(self, value):
        """Sets the value of the counter"""
        Counter.redis.set(self.name, value)

    @value.deleter
    def value(self):
        """Removes the counter fom the database"""
        Counter.redis.delete(self.name)

    def increment(self):
        """Increments the current value of the counter by 1"""
        return Counter.redis.incr(self.name)

    def serialize(self):
        """Converts a counter into a dictionary"""
        return {"name": self.name, "counter": self.value}

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################

    @classmethod
    def create(cls, name):
        """Atomically creates a new counter with a value of 0

        Returns:
            Counter: the new counter, or None if a counter with that
            name already exists
        """
        try:
            created = cls.redis.set(name, 0, nx=True)
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return cls(name, create=False) if created else None

    @classmethod
    def all(cls):
        """Returns all of the counters

        Uses SCAN (which does not block the server the way KEYS does) to
        collect the names and a single MGET to fetch every value, so the
        number of round trips does not grow with the number of counters.
        """
        try:
            # dict.fromkeys() de-duplicates: SCAN may return a key more than once
            names = list(dict.fromkeys(cls.redis.scan_iter("*", count=1000)))
            values = cls.redis.mget(names) if names else []
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return [
            {"name": name, "counter": int(value)}
            for name, value in zip(names, values)
            if value is not None  # key removed between SCAN and MGET
        ]

    @classmethod
    def find(cls, name):
        """Finds a counter with the name or returns None

        This is a read-only operation; it never writes to Redis.
        """
        try:
            exists = cls.redis.exists(name)
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return cls(name, create=False) if exists else None

    @classmethod
    def remove_all(cls):
        """Removes all of the keys in the database"""
        try:
            cls.redis.flushall()
        except Exception as err:
            raise DatabaseConnectionError(err) from err

    ######################################################################
    #  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
    ######################################################################

    @classmethod
    def test_connection(cls):
        """Test connection by pinging the host"""
        success = False
        try:
            cls.redis.ping()
            logger.info("Connection established")
            success = True
        except RedisConnectionError:
            logger.warning("Connection Error!")
        return success

    @classmethod
    def connect(cls, database_uri):
        """Establishes the database connection

        Arguments:
            database_uri: a uri to the Redis database (see service.config)

        Raises:
            DatabaseConnectionError: the uri is empty or Redis is unreachable
        """
        if not database_uri:
            msg = "No database URI was provided; check DATABASE_URI in service.config"
            logger.error(msg)
            raise DatabaseConnectionError(msg)

        logger.info("Attempting to connect to Redis...")

        cls.redis = Redis.from_url(
            database_uri, encoding="utf-8", decode_responses=True
        )

        if not cls.test_connection():
            # if you end up here, redis instance is down.
            cls.redis = None
            logger.fatal("*** FATAL ERROR: Could not connect to the Redis Service")
            raise DatabaseConnectionError("Could not connect to the Redis Service")

        logger.info("Successfully connected to Redis")
        return cls.redis
