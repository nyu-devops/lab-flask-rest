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
Counter Service

This service keeps track of named counters
"""
from flask import jsonify, url_for, abort
from service.models import Counter
from .common import status  # HTTP Status Codes

# Import Flask application
from . import app


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
#                 R E S T   A P I
############################################################

# -----------------------------------------------------------
# List counters
# -----------------------------------------------------------
@app.route("/counters", methods=["GET"])
def list_counters():
    """Lists all of the counters in the database

    Returns:
        list: an array of counter names
    """
    app.logger.info("Request to list all counters...")

    # Get the names of all of the counters
    counters = [counter.serialize() for counter in Counter.all()]
    return jsonify(counters)


# -----------------------------------------------------------
# Create counters
# -----------------------------------------------------------
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    """Creates a new counter and stores it in the database

    Args:
        name (str): the name of the counter to create

    Returns:
        dict: the counter and it's value
    """
    app.logger.info(f"Request to Create counter {name}...")

    # See if the counter already exists and send an error if it does
    counter = Counter.find(name)
    if counter is not None:
        abort(status.HTTP_409_CONFLICT, f"Counter {name} already exists")

    # Create the new counter
    counter = Counter(name)
    counter.create()

    # Set the location header and return the new counter
    location_url = url_for("read_counters", name=name, _external=True)
    return (
        jsonify(counter.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


# -----------------------------------------------------------
# Read counters
# -----------------------------------------------------------
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    """Reads a counter from the database

    Args:
        name (str): the name of the counter to read

    Returns:
        dict: the counter and it's value
    """
    app.logger.info(f"Request to Read counter {name}...")

    # Get the current counter
    counter = Counter.find(name)
    if counter is None:
        abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # Return the counter
    return jsonify(counter.serialize())


# -----------------------------------------------------------
# Update counters
# -----------------------------------------------------------
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    """Updates a counter in the database

    Args:
        name (str): the name of the counter to update

    Returns:
        dict: the counter and it's value
    """
    app.logger.info(f"Request to Update counter {name}...")

    # Get the current counter
    counter = Counter.find(name)
    if counter is None:
        abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # Increment the counter and return the new value
    counter.update()

    return jsonify(counter.serialize())


# -----------------------------------------------------------
# Delete counters
# -----------------------------------------------------------
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    """Delete a counter from the database

    Args:
        name (str): the name of the counter to delete

    Returns:
        str: always returns an empty string
    """
    app.logger.info(f"Request to Delete counter {name}...")

    # Get the current counter
    counter = Counter.find(name)
    # If it exists delete it, if not do nothing
    if counter is not None:
        counter.delete()

    # Delete always returns 204
    return "", status.HTTP_204_NO_CONTENT


# -----------------------------------------------------------
# Reset counters action
# -----------------------------------------------------------
@app.route("/counters/<name>/reset", methods=["PUT"])
def reset_counters(name):
    """Resets a counter back to zero

    Args:
        name (str): the name of the counter to reset

    Returns:
        dict: the counter and it's zero value
    """
    app.logger.info(f"Request to Reset counter {name}...")

    # Get the current counter
    counter = Counter.find(name)
    if counter is None:
        abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # reset the counter to zero
    counter.reset()

    return jsonify(counter.serialize())


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """Initializes the SQLAlchemy app"""
    # pylint: disable=invalid-name, global-variable-not-assigned
    global app
    Counter.init_db(app)
