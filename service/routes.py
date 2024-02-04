######################################################################
# Copyright (c) 2015, 2024 John J. Rofrano. All Rights Reserved.
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
Counter Service

This service keeps track of named counters
"""

import os
from flask import jsonify, abort, url_for
from flask import current_app as app
from service.common import status  # HTTP Status Codes
from .models import Counter, DatabaseConnectionError

DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = os.getenv("PORT", "8080")


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Counter Service REST API",
            version="1.0",
            paths=url_for("list_counters", _external=True),
        ),
        status.HTTP_200_OK,
    )


############################################################
# List counters
############################################################
@app.route("/counters", methods=["GET"])
def list_counters():
    """List counters"""
    app.logger.info("Request to list all counters...")
    try:
        counters = Counter.all()
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return jsonify(counters)


############################################################
# Read counters
############################################################
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    """Read a counter"""
    app.logger.info("Request to Read counter: %s...", name)

    try:
        counter = Counter.find(name)
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    if not counter:
        abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    app.logger.info("Returning: %d...", counter.value)
    return jsonify(counter.serialize())


############################################################
# Create counter
############################################################
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    """Create a counter"""
    app.logger.info("Request to Create counter...")
    try:
        counter = Counter.find(name)
        if counter is not None:
            return jsonify(code=status.HTTP_409_CONFLICT, error="Counter already exists"), status.HTTP_409_CONFLICT

        counter = Counter(name)
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    location_url = url_for("read_counters", name=name, _external=True)
    return (
        jsonify(counter.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


############################################################
# Update counters
############################################################
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    """Update a counter"""
    app.logger.info("Request to Update counter...")
    try:
        counter = Counter.find(name)
        if counter is None:
            return jsonify(code=status.HTTP_404_NOT_FOUND, error=f"Counter {name} does not exist"), status.HTTP_404_NOT_FOUND

        count = counter.increment()
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return jsonify(name=name, counter=count)


############################################################
# Delete counters
############################################################
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    """Delete a counter"""
    app.logger.info("Request to Delete counter...")
    try:
        counter = Counter.find(name)
        if counter:
            del counter.value
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return "", status.HTTP_204_NO_CONTENT
