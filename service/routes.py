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
Pet Store Service

Paths:
------
GET /pets - Returns a list all of the Pets
GET /pets/{id} - Returns the Pet with a given id number
POST /pets - creates a new Pet record in the database
PUT /pets/{id} - updates a Pet record in the database
DELETE /pets/{id} - deletes a Pet record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Pet, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Pet Demo REST API Service",
            version="1.0",
            paths=url_for("list_pets", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL PETS
######################################################################
@app.route("/pets", methods=["GET"])
def list_pets():
    """ Returns all of the Pets """
    app.logger.info("Request for pet list")
    pets = []
    category = request.args.get("category")
    name = request.args.get("name")
    if category:
        pets = Pet.find_by_category(category)
    elif name:
        pets = Pet.find_by_name(name)
    else:
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["GET"])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    app.logger.info("Request for pet with id: %s", pet_id)
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(pet_id))
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW PET
######################################################################
@app.route("/pets", methods=["POST"])
def create_pets():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    app.logger.info("Request to create a pet")
    check_content_type("application/json")
    pet = Pet()
    pet.deserialize(request.get_json())
    pet.create()
    message = pet.serialize()
    location_url = url_for("get_pets", pet_id=pet.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["PUT"])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    app.logger.info("Request to update pet with id: %s", pet_id)
    check_content_type("application/json")
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(pet_id))
    pet.deserialize(request.get_json())
    pet.id = pet_id
    pet.update()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    app.logger.info("Request to delete pet with id: %s", pet_id)
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Pet.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))
