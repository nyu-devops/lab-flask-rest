# -*- coding: utf-8 -*-
# Copyright status.HTTP_201_CREATED6, 2020 John J. Rofrano. All Rights Reserved.
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

"""
Counter API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Counter, DatabaseConnectionError
from service.common import status

# logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")


######################################################################
#  T E S T   C A S E S
######################################################################
class ServiceTest(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.testing = True
        app.debug = False

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        Counter.connect(DATABASE_URI)
        Counter.remove_all()
        self.app = app.test_client()

    def tearDown(self):
        """This runs after each test"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should return the home page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_counter(self):
        """It should Create a counter"""
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["counter"], 0)

    def test_counter_already_exists(self):
        """It should not Counter that already exists"""
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_list_counters(self):
        """It should Get multiple counters"""
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.post("/counters/bar")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_counter(self):
        """It should Get a counter"""
        self.test_create_counter()
        resp = self.app.get("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["counter"], 0)

    def test_get_counter_not_found(self):
        """It should not return a counter that does not exist"""
        resp = self.app.get("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_counter_not_found(self):
        """It should not update a counter that does not exist"""
        resp = self.app.put("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_increment_counter(self):
        """It should Increment the counter"""
        self.test_get_counter()
        resp = self.app.put("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["counter"], 1)

        resp = self.app.put("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["counter"], 2)

    def test_delete_counter(self):
        """It should Delete the counter"""
        self.test_create_counter()
        resp = self.app.delete("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_method_not_allowed(self):
        """It should not allow usuported Methods"""
        resp = self.app.post("/counters")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  T E S T   E R R O R   H A N D L E R S
    ######################################################################

    @patch("service.routes.Counter.redis.get")
    def test_failed_get_request(self, redis_mock):
        """It should handle Error for failed GET"""
        redis_mock.return_value = 0
        redis_mock.side_effect = DatabaseConnectionError()
        resp = self.app.get("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.models.Counter.increment")
    def test_failed_update_request(self, value_mock):
        """It should handle Error for failed UPDATE"""
        value_mock.return_value = 0
        value_mock.side_effect = DatabaseConnectionError()
        self.test_create_counter()
        resp = self.app.put("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.models.Counter.__init__")
    def test_failed_post_request(self, value_mock):
        """It should handle Error for failed POST"""
        value_mock.return_value = 0
        value_mock.side_effect = DatabaseConnectionError()
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.routes.Counter.redis.keys")
    def test_failed_list_request(self, redis_mock):
        """It should handle Error for failed LIST"""
        redis_mock.return_value = 0
        redis_mock.side_effect = Exception()
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_failed_delete_request(self):
        """It should handle Error for failed DELETE"""
        self.test_create_counter()
        with patch("service.routes.Counter.redis.get") as redis_mock:
            redis_mock.return_value = 0
            redis_mock.side_effect = DatabaseConnectionError()
            resp = self.app.delete("/counters/foo")
            self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
