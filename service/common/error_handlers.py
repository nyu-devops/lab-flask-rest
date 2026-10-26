######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
Error Handlers

This module contains error handlers functions to send back errors as json
"""
from flask import jsonify
from flask import current_app as app
from service.common import status
from service.models import DatabaseConnectionError
from service.validators import ValidationError

######################################################################
# Error Handlers
######################################################################


@app.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """Handles database connection errors with 503_SERVICE_UNAVAILABLE"""
    return service_unavailable(error)


@app.errorhandler(ValidationError)
def request_validation_error(error):
    """Handles input that fails validation with 400_BAD_REQUEST"""
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """Handles bad requests with 400_BAD_REQUEST"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=message,
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Handles resources not found with 404_NOT_FOUND"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """Handles unsupported HTTP methods with 405_METHOD_NOT_SUPPORTED"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Handles unexpected server error with 500_SERVER_ERROR"""
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.errorhandler(status.HTTP_503_SERVICE_UNAVAILABLE)
def service_unavailable(error):
    """Handles unexpected server error with 503_SERVICE_UNAVAILABLE"""
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            error="Service is unavailable",
            message=message,
        ),
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )
