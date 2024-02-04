# -*- coding: utf-8 -*-
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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

# pylint: disable=disallowed-name
"""
Test cases for Counter Model

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from redis.exceptions import ConnectionError as RedisConnectionError
from service.models import Counter, DatabaseConnectionError

DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")

logging.disable(logging.CRITICAL)


######################################################################
#  T E S T   C A S E S
######################################################################
class CounterTests(TestCase):
    """Counter Model Tests"""

    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        # Counter.connect(DATABASE_URI)

    def setUp(self):
        """This runs before each test"""
        Counter.connect(DATABASE_URI)
        Counter.remove_all()
        self.counter = Counter()

    def tearDown(self):
        """This runs after each test"""
        # Counter.redis.flushall()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_counter_with_name(self):
        """It should Create a counter with a name"""
        counter = Counter("foo")
        self.assertIsNotNone(counter)
        self.assertEqual(counter.name, "foo")
        self.assertEqual(counter.value, 0)

    def test_create_counter_no_name(self):
        """It should not Create a counter without a name"""
        self.assertIsNotNone(self.counter)
        self.assertEqual(self.counter.name, "hits")
        self.assertEqual(self.counter.value, 0)

    def test_serialize_counter(self):
        """It should Serialize a counter"""
        self.assertIsNotNone(self.counter)
        data = self.counter.serialize()
        self.assertEqual(data["name"], "hits")
        self.assertEqual(data["counter"], 0)

    def test_set_list_counters(self):
        """It should List all of the counters"""
        _ = Counter("foo")
        _ = Counter("bar")
        counters = Counter.all()
        self.assertEqual(len(counters), 3)

    def test_set_find_counter(self):
        """It should Find a counter"""
        _ = Counter("foo")
        _ = Counter("bar")
        foo = Counter.find("foo")
        self.assertEqual(foo.name, "foo")

    def test_counter_not_found(self):
        """It should not find a counter"""
        foo = Counter.find("foo")
        self.assertIsNone(foo)

    def test_set_get_counter(self):
        """It should Set and then Get the counter"""
        self.counter.value = 13
        self.assertEqual(self.counter.value, 13)

    def test_delete_counter(self):
        """It should Delete a counter"""
        counter = Counter("foo")
        self.assertEqual(counter.value, 0)
        del counter.value
        found = Counter.find("foo")
        self.assertIsNone(found)

        self.assertEqual(self.counter.value, 0)

    def test_increment_counter(self):
        """It should Increment the current value of the counter by 1"""
        count = self.counter.value
        next_count = self.counter.increment()
        logging.debug(
            "count(%s) = %s, next_count(%s) = %s",
            type(count),
            count,
            type(next_count),
            next_count,
        )
        self.assertEqual(next_count, count + 1)

    def test_increment_counter_to_2(self):
        """It should Increment the counter to 2"""
        self.assertEqual(self.counter.value, 0)
        self.counter.increment()
        self.assertEqual(self.counter.value, 1)
        counter = Counter.find("hits")
        counter.increment()
        self.assertEqual(counter.value, 2)

    @patch("redis.Redis.ping")
    def test_no_connection(self, ping_mock):
        """It should Handle a failed connection"""
        ping_mock.side_effect = RedisConnectionError()
        self.assertRaises(DatabaseConnectionError, self.counter.connect, DATABASE_URI)

    @patch.dict(os.environ, {"DATABASE_URI": ""})
    def test_missing_environment_creds(self):
        """It should detect Missing environment credentials"""
        self.assertRaises(DatabaseConnectionError, self.counter.connect)
