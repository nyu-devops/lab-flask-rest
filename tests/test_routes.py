"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import Counter
from service.common import status  # HTTP Status Codes

TEST_COUNTER = "foo"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.testing = True
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        Counter.remove_all()
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  T E S T   C A S E S 
######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_counters(self):
        """ It should Create a counter """
        resp = self.app.post(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["count"], 0)

    def test_list_counters(self):
        """ It should List counters """
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        # create a counter and name sure it appears in the list
        self.app.post("/counters/foo")
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

    def test_read_counters(self):
        """ It should Read a counter """
        self.test_create_counters()
        resp = self.app.get(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["count"], 0)

    def test_update_counters(self):
        """ It should Update a counter """
        self.test_read_counters()
        # now update it
        resp = self.app.put(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["count"], 1)

    def test_delete_counters(self):
        """ It should Delete a counter """
        self.test_create_counters()
        resp = self.app.delete(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.app.get(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_counter_already_exists(self):
        """ It should detect counter already exists """
        self.test_create_counters()
        resp = self.app.post(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_unknown_counter(self):
        """ It should not Update a counter that doesn't exist """
        resp = self.app.put("/counters/bar")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_reset_counter(self):
        """ It should Reset a counter """
        self.test_create_counters()
        # update counter to 3
        resp = self.app.put(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.put(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.put(f"/counters/{TEST_COUNTER}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["count"], 3)
        # reset counter to zero
        resp = self.app.put(f"/counters/{TEST_COUNTER}/reset")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], TEST_COUNTER)
        self.assertEqual(data["count"], 0)

    def test_reset_unknown_counter(self):
        """ It should not Reset a counter that doesn't exist """
        resp = self.app.put(f"/counters/{TEST_COUNTER}/reset")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed_handler(self):
        """ It should trigger Method Not Allowed error handler """
        resp = self.app.get(f"/counters/{TEST_COUNTER}/reset")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
