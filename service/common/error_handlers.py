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

Every error the service returns has the same JSON shape:

    {"status": <code>, "error": <short label>, "message": <details>}

Handlers are registered from the _ERRORS table below rather than written
out one by one, so adding support for a new status code is a single line.
"""
from functools import partial
from flask import jsonify
from flask import current_app as app
from service.common import status
from service.models import DatabaseConnectionError
from service.validators import ValidationError

# status code -> (label sent to the client, logger method used to record it)
_ERRORS = {
    status.HTTP_400_BAD_REQUEST: ("Bad Request", "warning"),
    status.HTTP_404_NOT_FOUND: ("Not Found", "warning"),
    status.HTTP_405_METHOD_NOT_ALLOWED: ("Method not Allowed", "warning"),
    status.HTTP_409_CONFLICT: ("Conflict", "warning"),
    status.HTTP_500_INTERNAL_SERVER_ERROR: ("Internal Server Error", "error"),
    status.HTTP_503_SERVICE_UNAVAILABLE: ("Service is unavailable", "error"),
}

# application exceptions -> the status code they should be reported as
_EXCEPTIONS = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    DatabaseConnectionError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def json_error(status_code, error):
    """Logs the error and returns it to the client as JSON"""
    label, log_level = _ERRORS[status_code]
    message = str(error)
    getattr(app.logger, log_level)(message)
    return (
        jsonify(status=status_code, error=label, message=message),
        status_code,
    )


######################################################################
# Register the handlers
######################################################################
for _code in _ERRORS:
    app.register_error_handler(_code, partial(json_error, _code))

for _exception, _code in _EXCEPTIONS.items():
    app.register_error_handler(_exception, partial(json_error, _code))
