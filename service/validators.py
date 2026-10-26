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
Input Validators

This module contains the validation rules for data that comes in from
the outside world (e.g. the counter name in the URL) so that the routes
can reject bad input *before* touching the database.

Counter name rules:
    * must be a string
    * must not be empty or consist only of whitespace
    * must be between MIN_NAME_LENGTH and MAX_NAME_LENGTH characters long
    * may only contain ASCII letters, digits, hyphens (-) and underscores (_)
"""
import re

# Length constraints (inclusive)
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 50

# Only letters, numbers, hyphens, and underscores are allowed
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

ALLOWED_CHARACTERS_DESCRIPTION = "letters, numbers, hyphens (-), and underscores (_)"


class ValidationError(ValueError):
    """Raised when user supplied input fails validation"""


def validate_counter_name(name) -> str:
    """Validates a counter name and returns it if it is acceptable

    Arguments:
        name: the counter name to validate

    Returns:
        str: the validated name (unchanged)

    Raises:
        ValidationError: with a human readable reason if the name is invalid
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Counter name must be a string, not {type(name).__name__}"
        )

    if not name.strip():
        raise ValidationError("Counter name must not be empty or contain only whitespace")

    length = len(name)
    if length < MIN_NAME_LENGTH or length > MAX_NAME_LENGTH:
        raise ValidationError(
            f"Counter name must be between {MIN_NAME_LENGTH} and "
            f"{MAX_NAME_LENGTH} characters long, but '{name}' is {length} characters"
        )

    if not NAME_PATTERN.match(name):
        raise ValidationError(
            f"Counter name '{name}' contains invalid characters; "
            f"only {ALLOWED_CHARACTERS_DESCRIPTION} are allowed"
        )

    return name


def is_valid_counter_name(name) -> bool:
    """Returns True if the name passes validation, otherwise False

    This is a convenience wrapper around validate_counter_name() for
    callers that only want a yes/no answer rather than an exception.
    """
    try:
        validate_counter_name(name)
    except ValidationError:
        return False
    return True
