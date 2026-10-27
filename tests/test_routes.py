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
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Counter, DatabaseConnectionError
from service.common import status
from service.validators import MAX_NAME_LENGTH
from tests import TEST_DATABASE_URI

# logging.disable(logging.CRITICAL)


######################################################################
#  T E S T   C A S E S
######################################################################
class ServiceTest(TestCase):  # pylint: disable=too-many-public-methods
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.testing = True
        app.debug = False
        Counter.connect(TEST_DATABASE_URI)

    def setUp(self):
        """This runs before each test"""
        Counter.remove_all()
        self.app = app.test_client()

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
    #  T E S T   N A M E   V A L I D A T I O N
    ######################################################################

    def assert_bad_request(self, resp, expected_fragment):
        """Asserts a 400 JSON error response with a helpful message"""
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertEqual(data["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn(expected_fragment, data["message"])

    def test_create_counter_with_hyphens_and_underscores(self):
        """It should Create counters whose names contain - and _"""
        for name in ["foo-bar", "foo_bar", "foo-bar_baz-1", "-", "_"]:
            with self.subTest(name=name):
                resp = self.app.post(f"/counters/{name}")
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.assertEqual(resp.get_json()["name"], name)

    def test_create_counter_with_numbers_and_mixed_case(self):
        """It should Create counters with digits and upper case letters"""
        for name in ["123", "Foo", "FOO", "f00"]:
            with self.subTest(name=name):
                resp = self.app.post(f"/counters/{name}")
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.assertEqual(resp.get_json()["name"], name)

    def test_create_counter_single_character_name(self):
        """It should Create a counter with a one character name"""
        resp = self.app.post("/counters/a")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.get_json()["name"], "a")

    def test_create_counter_max_length_name(self):
        """It should Create a counter with a name of exactly 50 characters"""
        name = "a" * MAX_NAME_LENGTH
        resp = self.app.post(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.get_json()["name"], name)
        # and the full CRUD cycle should work with it
        resp = self.app.get(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.put(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.delete(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_counter_name_too_long(self):
        """It should not Create a counter with a name over 50 characters"""
        name = "a" * (MAX_NAME_LENGTH + 1)
        resp = self.app.post(f"/counters/{name}")
        self.assert_bad_request(resp, f"between 1 and {MAX_NAME_LENGTH} characters")
        # nothing should have been created
        resp = self.app.get("/counters")
        self.assertEqual(resp.get_json(), [])

    def test_create_counter_whitespace_only_name(self):
        """It should not Create a counter whose name is only whitespace"""
        for path in ["/counters/%20", "/counters/%20%20%20", "/counters/%09"]:
            with self.subTest(path=path):
                resp = self.app.post(path)
                self.assert_bad_request(resp, "must not be empty or contain only whitespace")
        resp = self.app.get("/counters")
        self.assertEqual(resp.get_json(), [])

    def test_create_counter_name_with_spaces(self):
        """It should not Create a counter with spaces in the name"""
        for path in ["/counters/foo%20bar", "/counters/%20foo", "/counters/foo%20"]:
            with self.subTest(path=path):
                resp = self.app.post(path)
                self.assert_bad_request(resp, "invalid characters")

    def test_create_counter_name_with_special_characters(self):
        """It should not Create a counter with punctuation or symbols in the name"""
        for name in ["foo!", "foo.bar", "foo@bar", "foo%24", "foo%3Bbar", "%7Bfoo%7D"]:
            with self.subTest(name=name):
                resp = self.app.post(f"/counters/{name}")
                self.assert_bad_request(resp, "invalid characters")

    def test_create_counter_name_with_unicode(self):
        """It should not Create a counter with non-ASCII characters in the name"""
        resp = self.app.post("/counters/caf%C3%A9")
        self.assert_bad_request(resp, "invalid characters")
        self.assertIn("café", resp.get_json()["message"])

    def test_create_counter_empty_name(self):
        """It should not Create a counter with an empty name"""
        # An empty name never reaches the handler: there is no route for it
        resp = self.app.post("/counters/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_counter_invalid_name(self):
        """It should not Read a counter with an invalid name"""
        resp = self.app.get("/counters/foo!")
        self.assert_bad_request(resp, "invalid characters")
        resp = self.app.get("/counters/%20")
        self.assert_bad_request(resp, "must not be empty")
        resp = self.app.get(f"/counters/{'a' * (MAX_NAME_LENGTH + 1)}")
        self.assert_bad_request(resp, "characters long")

    def test_update_counter_invalid_name(self):
        """It should not Update a counter with an invalid name"""
        resp = self.app.put("/counters/foo!")
        self.assert_bad_request(resp, "invalid characters")
        resp = self.app.put("/counters/%20")
        self.assert_bad_request(resp, "must not be empty")
        resp = self.app.put(f"/counters/{'a' * (MAX_NAME_LENGTH + 1)}")
        self.assert_bad_request(resp, "characters long")

    def test_delete_counter_invalid_name(self):
        """It should not Delete a counter with an invalid name"""
        # DELETE is normally idempotent (204 even if missing) but an
        # invalid name is a client error and should be reported
        resp = self.app.delete("/counters/foo!")
        self.assert_bad_request(resp, "invalid characters")
        resp = self.app.delete("/counters/%20")
        self.assert_bad_request(resp, "must not be empty")
        resp = self.app.delete(f"/counters/{'a' * (MAX_NAME_LENGTH + 1)}")
        self.assert_bad_request(resp, "characters long")

    def test_invalid_name_is_rejected_before_database_access(self):
        """It should validate the name before touching the database"""
        with patch("service.routes.Counter.find") as find_mock:
            for method in ["post", "get", "put", "delete"]:
                with self.subTest(method=method):
                    resp = getattr(self.app, method)("/counters/not%20valid")
                    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            find_mock.assert_not_called()

    def test_invalid_name_takes_precedence_over_not_found(self):
        """It should return 400 not 404 for an invalid name that does not exist"""
        resp = self.app.get("/counters/does-not-exist!")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.app.put("/counters/does-not-exist!")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_request_message_is_helpful(self):
        """It should explain what is wrong and what is allowed"""
        resp = self.app.post("/counters/bad%20name")
        message = resp.get_json()["message"]
        self.assertIn("'bad name'", message)
        self.assertIn("letters", message)
        self.assertIn("numbers", message)
        self.assertIn("hyphens", message)
        self.assertIn("underscores", message)

    ######################################################################
    #  T E S T   E R R O R   H A N D L E R S
    ######################################################################

    @patch("service.routes.Counter.find")
    def test_failed_get_request(self, find_mock):
        """It should handle Error for failed GET"""
        find_mock.side_effect = DatabaseConnectionError()
        resp = self.app.get("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.routes.Counter.increment")
    def test_failed_update_request(self, increment_mock):
        """It should handle Error for failed UPDATE"""
        increment_mock.side_effect = DatabaseConnectionError()
        self.test_create_counter()
        resp = self.app.put("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.routes.Counter.create")
    def test_failed_post_request(self, create_mock):
        """It should handle Error for failed POST"""
        create_mock.side_effect = DatabaseConnectionError()
        resp = self.app.post("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.routes.Counter.all")
    def test_failed_list_request(self, all_mock):
        """It should handle Error for failed LIST"""
        all_mock.side_effect = DatabaseConnectionError()
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("service.routes.Counter.find")
    def test_failed_delete_request(self, find_mock):
        """It should handle Error for failed DELETE"""
        find_mock.side_effect = DatabaseConnectionError()
        resp = self.app.delete("/counters/foo")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
