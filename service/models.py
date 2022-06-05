######################################################################
# Copyright (c) 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Models for Counter

All of the models are stored in this module
"""
import logging
from redis import Redis

logger = logging.getLogger("flask.app")


class Counter:
    """
    Class that represents a Counter
    """

    app = None
    counter = None

    def __init__(self, name: str, count: int = 0):
        """Constructor for Counter"""
        self.name = name
        self.count = count

    def __repr__(self):
        return f"<Counter {self.name} count=[{self.count}]>"

    def create(self):
        """
        Creates a Counter to the database
        """
        logger.info("Creating %s", self.name)
        self.counter.set(self.name, self.count)

    def update(self):
        """
        Updates a Counter to the database
        """
        logger.info("Saving %s", self.name)
        self.count = self.counter.incr(self.name)

    def delete(self):
        """Removes a Counter from the data store"""
        logger.info("Deleting %s", self.name)
        self.counter.delete(self.name)
        self.count = 0

    def reset(self):
        """
        Resets a Counter to zero
        """
        logger.info("Resetting %s", self.name)
        self.counter.set(self.name, 0)
        self.count = 0

    def serialize(self):
        """Serializes a Counter into a dictionary"""
        return {"name": self.name, "count": self.count}

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize Redis from the Flask app
        cls.counter = Redis.from_url(
            app.config["DATABASE_URI"], encoding="utf-8", decode_responses=True
        )

    @classmethod
    def all(cls) -> list:
        """Returns all of the Counters in the database"""
        logger.info("Processing all Counters")
        return [
            Counter(name, int(cls.counter.get(name))) for name in cls.counter.keys("*")
        ]

    @classmethod
    def find(cls, name: str):
        """Finds a Counter by it's name"""
        logger.info("Processing lookup for name %s ...", name)
        count = cls.counter.get(name)
        if not count:
            return None
        return Counter(name, int(count))

    @classmethod
    def remove_all(cls) -> None:
        """Removes all counters from the database"""
        logger.info("Request to Remove all counters...")
        if cls.app.testing:
            logger.info("Removing all counters")
            cls.counter.flushall()
        else:
            logger.warning("Cannot Remove all counters, system not under test")
