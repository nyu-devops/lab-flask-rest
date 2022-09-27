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
            # paths=url_for("list_counters", _external=True),
        ),
        status.HTTP_200_OK,
    )


############################################################
#                 R E S T   A P I
############################################################

# -----------------------------------------------------------
# List counters
# -----------------------------------------------------------


# -----------------------------------------------------------
# Create counters
# -----------------------------------------------------------


# -----------------------------------------------------------
# Read counters
# -----------------------------------------------------------

# -----------------------------------------------------------
# Update counters
# -----------------------------------------------------------

# -----------------------------------------------------------
# Delete counters
# -----------------------------------------------------------


# -----------------------------------------------------------
# Reset counters action
# -----------------------------------------------------------
