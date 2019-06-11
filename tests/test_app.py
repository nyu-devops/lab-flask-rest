# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Test cases for the Pet Service

Run with:
  nosetests
  coverage report -m
"""

import os
import unittest
from flask_api import status    # HTTP Status Codes
from app import app, db, Pet

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db/test.db')

class TestPetService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    def setUp(self):
        """ Runs before each test """
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        Pet(name='fido', category='dog').save()
        Pet(name='kitty', category='cat').save()
        self.app = app.test_client()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Pet Demo REST API Service')

    def test_create_pet(self):
        """ Create a Pet """
        # add a new pet
        pet = dict(name='sammy', category='snake')
        resp = self.app.post('/pets',
                             json=pet,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_pet = resp.get_json()
        self.assertEqual(new_pet['name'], 'sammy')
        self.assertEqual(new_pet['category'], 'snake')

    def test_get_pet_list(self):
        """ Get a list of Pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_pet(self):
        """ Get one Pet """
        resp = self.app.get('/pets/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'kitty')

    def test_get_pet_not_found(self):
        """ Get a Pet thats not found """
        resp = self.app.get('/pets/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_spoof_pet_id(self):
        """ Create a Pet passing in an id """
        # add a new pet
        pet = dict(id=999, name='sammy', category='snake')
        resp = self.app.post('/pets', json=pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'sammy')
        self.assertNotEqual(new_json['id'], 999)

    def test_update_pet(self):
        """ Update a Pet """
        kitty = dict(name='kitty', category='tabby')
        resp = self.app.put('/pets/2', json=kitty, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_kitty = resp.get_json()
        self.assertEqual(new_kitty['category'], 'tabby')

    def test_update_pet_with_no_name(self):
        """ Update a Pet with no name """
        pet = dict(category='dog')
        resp = self.app.put('/pets/2', json=pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """ Update a Pet that can't be found """
        pet = dict(name='timothy', category='mouse')
        resp = self.app.put('/pets/0', json=pet, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_pet(self):
        """ Delete a Pet that exists """
        resp = self.app.delete('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

    def test_create_pet_with_no_name(self):
        """ Create a Pet with the name missing """
        pet = dict(category='dog')
        resp = self.app.post('/pets', json=pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_pet(self):
        """ Get a Pet that doesn't exist """
        resp = self.app.get('/pets/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_pet_list_by_category(self):
        """ Query Pets by Category """
        resp = self.app.get('/pets', query_string='category=dog')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue(b'fido' in resp.data)
        self.assertFalse(b'kitty' in resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['category'], 'dog')

    def test_method_not_allowed(self):
        """ Call a Method thats not Allowed """
        resp = self.app.post('/pets/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
