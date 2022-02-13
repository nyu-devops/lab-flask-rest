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
Hit Counter REST API Demonstration
"""
import os
from redis import Redis
from flask import Flask, jsonify, url_for, abort

app = Flask(__name__)

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "redis://localhost:6379")

counter = Redis.from_url(DATABASE_URI, encoding="utf-8", decode_responses=True)

# HTTP RETURN CODES
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

############################################################
#            E R R O R   H A N D L E R S
# ----------------------------------------------------------
# REST API's should only return json so we override the
# existing HTML error handlers to return json
############################################################
@app.errorhandler(HTTP_404_NOT_FOUND)
def not_found(error):
    """Handles resources not found with 404_NOT_FOUND"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=HTTP_404_NOT_FOUND, error="Not Found", message=message),
        HTTP_404_NOT_FOUND,
    )


@app.errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(HTTP_409_CONFLICT)
def method_not_supported(error):
    """Handles database conflicts with HTTP_409_CONFLICT"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=HTTP_409_CONFLICT, error="Conflict", message=message),
        HTTP_409_CONFLICT,
    )


############################################################
# Index page (Home page)
############################################################
@app.route("/")
def index():
    """Returns information about the service"""
    app.logger.info("Request for Base URL")
    return jsonify(
        status=HTTP_200_OK,
        message="Hit Counter Service",
        version="1.0.0",
        url=url_for("list_counters", _external=True),
    )


############################################################
#                 R E S T   A P I
############################################################


#-----------------------------------------------------------
# List counters
#-----------------------------------------------------------
@app.route("/counters", methods=["GET"])
def list_counters():
    """Lists all of the counters in the database

    Returns:
        list: an array of counter names
    """
    app.logger.info("Request to list all counters...")

    # Get the database key names as a list
    names = counter.keys("*")
    return jsonify(names)


#-----------------------------------------------------------
# Create counters
#-----------------------------------------------------------
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
    count = counter.get(name)
    if count is not None:
        abort(HTTP_409_CONFLICT, f"Counter {name} already exists")

    # Create the new counter and set it to zero
    counter.set(name, 0)

    # Set the location header and return the new counter
    location_url = url_for("read_counters", name=name, _external=True)
    return (
        jsonify(name=name, counter=0),
        HTTP_201_CREATED,
        {"Location": location_url},
    )


#-----------------------------------------------------------
# Read counters
#-----------------------------------------------------------
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
    count = counter.get(name)

    # Send an error if it does not exist
    if count is None:
        abort(HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # Return the counter
    return jsonify(name=name, counter=int(count))


#-----------------------------------------------------------
# Update counters
#-----------------------------------------------------------
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    """Updates a ciunter in the database

    Args:
        name (str): the name of the counter to update

    Returns:
        dict: the counter and it's value
    """
    app.logger.info(f"Request to Update counter {name}...")

    # Get the current counter
    count = counter.get(name)

    # Send an error if it does not exist
    if count is None:
        abort(HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # Increment the counter and return the new value
    count = counter.incr(name)
    return jsonify(name=name, counter=count)


#-----------------------------------------------------------
# Delete counters
#-----------------------------------------------------------
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
    count = counter.get(name)

    # If it exists delete it, if not do nothing
    if count is not None:
        counter.delete(name)

    # Delete always returns 204
    return "", HTTP_204_NO_CONTENT


#-----------------------------------------------------------
# Reset counters action
#-----------------------------------------------------------
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
    count = counter.get(name)

    # Send an error if it does not exist
    if count is None:
        abort(HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    # reset the counter to zero
    counter.set(name, 0)

    # Get the new value and return it
    count = int(counter.get(name))  # Redis stores all values and strings :(
    return jsonify(name=name, counter=count)


############################################################
#          U T I L I T Y   F U N C T I O N S
############################################################

def remove_counters():
    """Utility function to flush the database for testing"""    
    global counter
    if app.testing:
        counter.flushall()
