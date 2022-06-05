"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from service import app
from service.models import Counter

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "redis://localhost:6379")
TEST_COUNTER = "foo"

######################################################################
#  C O U N T E R   M O D E L   T E S T   C A S E S
######################################################################
class TestCounterModel(unittest.TestCase):
    """ Test Cases for Counter Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Counter.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        Counter.remove_all()

    def tearDown(self):
        """ This runs after each test """
        pass

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_counter(self):
        """ It should create a counter """
        counter = Counter(TEST_COUNTER)
        counter.create()
        self.assertEqual(counter.name, TEST_COUNTER)
        self.assertEqual(counter.count, 0)

    def test_read_a_counter(self):
        """ It should read a counter """
        counter = Counter(TEST_COUNTER)
        counter.create()
        results = Counter.find(TEST_COUNTER)
        self.assertEqual(results.name, TEST_COUNTER)
        self.assertEqual(results.count, 0)

    def test_update_a_counter(self):
        """ It should update a counter """
        counter = Counter(TEST_COUNTER)
        counter.create()
        counter.update()
        self.assertEqual(counter.name, TEST_COUNTER)
        self.assertEqual(counter.count, 1)

    def test_list_a_counter(self):
        """ It should list counters """
        Counter(TEST_COUNTER).create()
        Counter("bar").create()
        Counter("baz").create()
        results = Counter.all()
        self.assertEqual(len(results), 3)

    def test_delete_a_counter(self):
        """ It should delete a counter """
        counter = Counter(TEST_COUNTER)
        counter.create()
        results = Counter.find(TEST_COUNTER)
        self.assertEqual(results.name, TEST_COUNTER)
        counter.delete()
        results = Counter.find(TEST_COUNTER)
        self.assertIsNone(results)

    def test_reset_a_counter(self):
        """ It should reset a counter """
        counter = Counter(TEST_COUNTER)
        counter.create()
        # update it to 2
        counter.update()
        counter.update()
        self.assertEqual(counter.name, TEST_COUNTER)
        self.assertEqual(counter.count, 2)
        # reset the counter
        counter.reset()
        # assert that the in-memory object was reset
        self.assertEqual(counter.count, 0)
        # fetch it from the database and check again
        results = Counter.find(TEST_COUNTER)
        self.assertEqual(results.name, TEST_COUNTER)
        self.assertEqual(counter.count, 0)

    def test_serialize_a_counter(self):
        """ It should serialize a counter """
        counter = Counter(TEST_COUNTER)
        results = counter.serialize()
        self.assertEqual(results["name"], TEST_COUNTER)
        self.assertEqual(results["count"], 0)

    def test_repr_a_counter(self):
        """ It should represent a counter """
        counter = Counter(TEST_COUNTER)
        self.assertEqual(str(counter), f"<Counter {TEST_COUNTER} count=[0]>")
