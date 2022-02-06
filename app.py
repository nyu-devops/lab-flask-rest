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
from flask import Flask, jsonify, url_for

DATABASE_URI = os.getenv("DATABASE_URI", "redis://localhost:6379")

app = Flask(__name__)

counter = Redis.from_url(DATABASE_URI, encoding="utf-8", decode_responses=True)

############################################################
# Index page
############################################################
@app.route("/")
def index():
    app.logger.info("Request for Base URL")
    return jsonify(
        status=200,
        message="Hit Counter Service",
        version="1.0.0",
        url=url_for("list_counters", _external=True),
    )


############################################################
# List counters
############################################################
@app.route("/counters", methods=["GET"])
def list_counters():
    app.logger.info("Request to list all counters...")
    counters = [
        dict(name=key, counter=int(counter.get(key))) for key in counter.keys("*")
    ]
    return jsonify(counters)


############################################################
# Create counters
############################################################
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    app.logger.info(f"Request to Create counter {name}...")
    count = counter.get(name)
    if count is not None:
        return jsonify(code=409, error="Counter already exists"), 409

    counter.set(name, 0)

    location_url = url_for("read_counters", name=name, _external=True)
    return jsonify(name=name, counter=0), 201, {"Location": location_url}


############################################################
# Read counters
############################################################
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    app.logger.info(f"Request to Read counter {name}...")
    count = counter.get(name)
    if count is None:
        return jsonify(code=404, error="Counter {} does not exist".format(name)), 404

    return jsonify(name=name, counter=int(count))


############################################################
# Update counters
############################################################
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    app.logger.info(f"Request to Update counter {name}...")
    count = counter.get(name)
    if count is None:
        return jsonify(code=404, error="Counter {} does not exist".format(name)), 404

    count = counter.incr(name)
    return jsonify(name=name, counter=count)


############################################################
# Delete counters
############################################################
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    app.logger.info(f"Request to Delete counter {name}...")
    count = counter.get(name)
    if count is not None:
        counter.delete(name)

    return "", 204


############################################################
# Reset counters action
############################################################
@app.route("/counters/<name>/reset", methods=["PUT"])
def reset_counters(name):
    app.logger.info(f"Request to Reset counter {name}...")
    count = counter.get(name)
    if count is None:
        return jsonify(code=404, error="Counter {} does not exist".format(name)), 404

    # reset the counter to zero
    counter.set(name, 0)
    count = int(counter.get(name))  # Redis stores all values and strings :(
    return jsonify(name=name, counter=count)


############################################################
# Utility for testing
############################################################
def remove_counters():
    global counter
    if app.testing:
        counter.flushall()
