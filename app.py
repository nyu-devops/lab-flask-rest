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
'''
Simple Flask REST API
'''
import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db/development.db')

# Create Flask application
app = Flask(__name__)

# We'll just use SQLite here so we don't need an external database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['LOGGING_LEVEL'] = logging.INFO

db = SQLAlchemy(app)

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(404)
def not_found(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), \
                   status.HTTP_404_NOT_FOUND

@app.errorhandler(400)
def bad_request(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported. Check your HTTP method and try again.'), \
                   status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(500)
def internal_error(error):
    return jsonify(status=500, error='Internal Server Error',
                   message='Houston... we have a problem.'), \
                   status.HTTP_500_INTERNAL_SERVER_ERROR

######################################################################
# Pet Model for database
######################################################################
class Pet(db.Model):
    """ Represents a single pet """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))

    def __repr__(self):
        return '<Pet %r>' % (self.name)

    def save(self):
        """ Saves an existing Pet in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes a Pet from the database """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return { "id": self.id, "name": self.name, "category": self.category }

    def deserialize(self, data):
        try:
            self.name = data['name']
            self.category = data['category']
        except KeyError as e:
            raise DataValidationError('Invalid pet: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid pet: body of request contained bad or no data')
        return self

    @classmethod
    def all(cls):
        """ Returns all of the Pets in the database """
        return cls.query.all()

    @classmethod
    def find(cls, pet_id):
        """ Finds a Pet by it's ID """
        return cls.query.get(pet_id)

    @classmethod
    def find_by_category(cls, category):
        """ Returns all of the Pets in a category """
        return cls.query.filter(cls.category == category)


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Pet Demo REST API Service',
                   version='1.0',
                   url=url_for('list_pets', _external=True)), status.HTTP_200_OK

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    results = []
    category = request.args.get('category')
    if category:
        app.logger.info('Getting Pets for category: {}'.format(category))
        results = Pet.find_by_category(category)
    else:
        app.logger.info('Getting all Pets')
        results = Pet.all()

    return jsonify([pet.serialize() for pet in results]), status.HTTP_200_OK

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pets(pet_id):
    app.logger.info('Getting Pet with id: {}'.format(pet_id))
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound('Pet with id: {} was not found'.format(pet_id))

    return jsonify(pet.serialize()), status.HTTP_200_OK

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pets():
    app.logger.info('Create Pet requested')
    pet = Pet()
    pet.deserialize(request.get_json())
    pet.save()
    app.logger.info('Created Pet with id: {}'.format(pet.id))
    return make_response(jsonify(pet.serialize()),
                         status.HTTP_201_CREATED,
                         {'Location': url_for('get_pets', pet_id=pet.id, _external=True)})

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pets(pet_id):
    app.logger.info('Updating with id: {}'.format(pet_id))
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound('Pet with id: {} was not found'.format(pet_id))

    # process the update request
    pet.deserialize(request.get_json())
    pet.id = pet_id # make id matches request
    pet.save()
    app.logger.info('Pet with id {} has been updated'.format(pet_id))
    return jsonify(pet.serialize()), status.HTTP_200_OK

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pets(pet_id):
    app.logger.info('Request to delete Pet with id: {}'.format(pet_id))
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def initialize():
    db.create_all()  # make our sqlalchemy tables
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        #logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(app.config['LOGGING_LEVEL'])
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(app.config['LOGGING_LEVEL'])
        app.logger.info('Logging handler established')


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print('Pet Service Starting...')
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
