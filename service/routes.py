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
from flask import jsonify, abort, url_for
from flask import current_app as app
from service.common import status  # HTTP Status Codes
from service.models import Counter


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
#           R E S T   A P I   M E T H O D S
############################################################


############################################################
# List counters
############################################################
@app.route("/counters", methods=["GET"])
def list_counters():
    """List counters"""
    app.logger.info("Request to list all counters...")

    counters = Counter.all()

    app.logger.info("Returning %d counters...", len(counters))
    return jsonify(counters)


############################################################
# Read counters
############################################################
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    """Read a counter"""
    app.logger.info("Request to Read counter: '%s'...", name)

    counter = Counter.find(name)

    if not counter:
        error(status.HTTP_404_NOT_FOUND, f"Counter '{name}' does not exist")

    app.logger.info("Returning: %d...", counter.value)
    return jsonify(counter.serialize())


############################################################
# Create counter
############################################################
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    """Create a counter"""
    app.logger.info("Request to Create counter: '%s'...", name)

    counter = Counter.find(name)
    if counter is not None:
        error(status.HTTP_409_CONFLICT, f"Counter '{name}' already exists")

    counter = Counter(name)

    location_url = url_for("read_counters", name=name, _external=True)
    app.logger.info("Counter '%s' created", name)
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
    app.logger.info("Request to Update counter: '%s'...", name)

    counter = Counter.find(name)
    if counter is None:
        error(status.HTTP_404_NOT_FOUND, f"Counter '{name}' does not exist")

    count = counter.increment()

    app.logger.info("Counter '%s' updated to %d", name, count)
    return jsonify(name=name, counter=count)


############################################################
# Delete counters
############################################################
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    """Delete a counter"""
    app.logger.info("Request to Delete counter: '%s'...", name)

    counter = Counter.find(name)
    if counter:
        del counter.value
        app.logger.info("Counter '%s' deleted", name)

    return "", status.HTTP_204_NO_CONTENT


############################################################
#         U T I L I T Y   F U N C T I O N S
############################################################


def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
