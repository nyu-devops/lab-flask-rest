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
import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)

DATABASE_URI = os.getenv("DATABASE_URI", "redis://localhost:6379")


class DatabaseConnectionError(RedisConnectionError):
    """Generic Exception for Redis database connection errors"""


class Counter:
    """An integer counter that is persisted in Redis

    You can establish a connection to Redis using an environment
    variable DATABASE_URI in the following format:

        DATABASE_URI="redis://userid:password@localhost:6379/0"

    This follows the same standards as SQLAlchemy URIs
    """

    redis = None

    def __init__(self, name: str = "hits", value: int = None):
        """Constructor"""
        self.name = name
        if not value:
            self.value = 0
        else:
            self.value = value

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
        return {
            "name": self.name,
            "counter": int(Counter.redis.get(self.name))
        }

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################

    @classmethod
    def all(cls):
        """Returns all of the counters"""
        try:
            counters = [
                {"name": key, "counter": int(cls.redis.get(key))}
                for key in cls.redis.keys("*")
            ]
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return counters

    @classmethod
    def find(cls, name):
        """Finds a counter with the name or returns None"""
        counter = None
        try:
            count = cls.redis.get(name)
            if count:
                counter = Counter(name, count)
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return counter

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
    def connect(cls, database_uri=None):
        """Established database connection

        Arguments:
            database_uri: a uri to the Redis database

        Raises:
            DatabaseConnectionError: Could not connect
        """
        if not database_uri:
            if "DATABASE_URI" in os.environ and os.environ["DATABASE_URI"]:
                database_uri = os.environ["DATABASE_URI"]
            else:
                msg = "DATABASE_URI is missing from environment."
                logger.error(msg)
                raise DatabaseConnectionError(msg)

        logger.info("Attempting to connecting to Redis...")

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
