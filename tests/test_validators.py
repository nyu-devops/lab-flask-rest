# -*- coding: utf-8 -*-
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

"""
Validator Test Suite

These are pure unit tests for service.validators and do not need
Flask or Redis. Test cases can be run with:
  pytest tests/test_validators.py
"""
from unittest import TestCase
from service.validators import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    ValidationError,
    validate_counter_name,
    is_valid_counter_name,
)


######################################################################
#  T E S T   C A S E S
######################################################################
class ValidateCounterNameTest(TestCase):  # pylint: disable=too-many-public-methods
    """Tests for validate_counter_name()"""

    def assert_invalid(self, name, expected_fragment):
        """Asserts that name is rejected and the message mentions why"""
        with self.assertRaises(ValidationError) as context:
            validate_counter_name(name)
        message = str(context.exception)
        self.assertIn(expected_fragment, message)
        return message

    ######################################################################
    #  V A L I D   N A M E S
    ######################################################################

    def test_simple_name(self):
        """It should accept a simple lowercase name"""
        self.assertEqual(validate_counter_name("foo"), "foo")

    def test_returns_name_unchanged(self):
        """It should return the name exactly as given"""
        name = "Mixed_Case-Name123"
        self.assertIs(validate_counter_name(name), name)

    def test_uppercase_and_mixed_case(self):
        """It should accept upper and mixed case letters"""
        for name in ["FOO", "Foo", "fooBAR"]:
            self.assertEqual(validate_counter_name(name), name)

    def test_numbers(self):
        """It should accept names that are only numbers or start with numbers"""
        for name in ["123", "1abc", "abc1"]:
            self.assertEqual(validate_counter_name(name), name)

    def test_hyphens_and_underscores(self):
        """It should accept hyphens and underscores anywhere in the name"""
        for name in ["foo-bar", "foo_bar", "-foo", "_foo", "foo-", "foo_", "-", "_", "a-b_c-d"]:
            self.assertEqual(validate_counter_name(name), name)

    def test_minimum_length(self):
        """It should accept a name of exactly the minimum length"""
        name = "a" * MIN_NAME_LENGTH
        self.assertEqual(validate_counter_name(name), name)

    def test_maximum_length(self):
        """It should accept a name of exactly the maximum length"""
        name = "a" * MAX_NAME_LENGTH
        self.assertEqual(len(name), 50)
        self.assertEqual(validate_counter_name(name), name)

    ######################################################################
    #  I N V A L I D   N A M E S
    ######################################################################

    def test_empty_string(self):
        """It should reject an empty string"""
        self.assert_invalid("", "must not be empty")

    def test_whitespace_only(self):
        """It should reject names that are only whitespace"""
        for name in [" ", "   ", "\t", "\n", " \t\n "]:
            self.assert_invalid(name, "must not be empty or contain only whitespace")

    def test_too_long(self):
        """It should reject a name one character over the maximum"""
        name = "a" * (MAX_NAME_LENGTH + 1)
        message = self.assert_invalid(name, f"between {MIN_NAME_LENGTH} and {MAX_NAME_LENGTH}")
        # The message should tell the caller how long the name actually was
        self.assertIn(f"{MAX_NAME_LENGTH + 1} characters", message)

    def test_much_too_long(self):
        """It should reject a name far over the maximum"""
        self.assert_invalid("a" * 1000, "1000 characters")

    def test_leading_or_trailing_whitespace(self):
        """It should reject names padded with whitespace"""
        for name in [" foo", "foo ", " foo "]:
            self.assert_invalid(name, "invalid characters")

    def test_embedded_whitespace(self):
        """It should reject names with whitespace in the middle"""
        for name in ["foo bar", "foo\tbar", "foo\nbar"]:
            self.assert_invalid(name, "invalid characters")

    def test_special_characters(self):
        """It should reject punctuation and symbols"""
        for char in "!@#$%^&*()+=[]{}|\\;:'\",.<>/?`~":
            self.assert_invalid(f"foo{char}bar", "invalid characters")

    def test_path_separators(self):
        """It should reject slashes and dots used in paths"""
        for name in ["foo/bar", "../foo", "foo.bar", "."]:
            self.assert_invalid(name, "invalid characters")

    def test_unicode_letters(self):
        """It should reject non-ASCII letters even though they are 'letters'"""
        for name in ["café", "naïve", "日本語", "Ω"]:
            self.assert_invalid(name, "invalid characters")

    def test_unicode_digits(self):
        """It should reject non-ASCII digits"""
        self.assert_invalid("١٢٣", "invalid characters")  # Arabic-Indic digits

    def test_invalid_message_includes_name(self):
        """It should include the offending name in the message"""
        message = self.assert_invalid("bad name!", "invalid characters")
        self.assertIn("'bad name!'", message)

    def test_invalid_message_lists_allowed_characters(self):
        """It should tell the caller which characters are allowed"""
        message = self.assert_invalid("bad!", "invalid characters")
        self.assertIn("letters", message)
        self.assertIn("numbers", message)
        self.assertIn("hyphens", message)
        self.assertIn("underscores", message)

    def test_none(self):
        """It should reject None"""
        self.assert_invalid(None, "must be a string")

    def test_non_string_types(self):
        """It should reject values that are not strings"""
        for value in [123, 1.5, b"foo", ["foo"], {"name": "foo"}, True]:
            message = self.assert_invalid(value, "must be a string")
            self.assertIn(type(value).__name__, message)

    def test_validation_error_is_a_value_error(self):
        """It should raise an exception that is also a ValueError"""
        with self.assertRaises(ValueError):
            validate_counter_name("")


class IsValidCounterNameTest(TestCase):
    """Tests for is_valid_counter_name()"""

    def test_valid_names_return_true(self):
        """It should return True for valid names"""
        for name in ["foo", "foo-bar_1", "A", "a" * MAX_NAME_LENGTH]:
            self.assertTrue(is_valid_counter_name(name), name)

    def test_invalid_names_return_false(self):
        """It should return False for invalid names"""
        for name in ["", " ", "foo bar", "foo!", "a" * (MAX_NAME_LENGTH + 1), None, 42]:
            self.assertFalse(is_valid_counter_name(name), repr(name))

    def test_does_not_raise(self):
        """It should never raise, even for garbage input"""
        try:
            is_valid_counter_name(object())
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.fail(f"is_valid_counter_name() raised {err!r}")
