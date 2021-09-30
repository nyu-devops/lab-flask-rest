# Copyright 2016, 2019 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Pet Demo Service

All of the models are stored in this module

Models
------
Pet - A Pet used in the Pet Store

Attributes:
-----------
name (string) - the name of the pet
category (string) - the category the pet belongs to (i.e., dog, cat)
available (boolean) - True for pets that are available for adoption

"""
import logging
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Gender(Enum):
    """ Enumeration of valid Pet Genders """
    Male = 0
    Female = 1
    Unknown = 3


class Pet(db.Model):
    """
    Class that represents a Pet

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app: Flask = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    gender = db.Column(
        db.Enum(Gender), nullable=False, server_default=(Gender.Unknown.name)
    )

    def __repr__(self) -> str:
        return "<Pet %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Pet to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Pet to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Pet from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """ Serializes a Pet into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "available": self.available,
            "gender": self.gender.name,  # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary

        Args:
            data (dict): A dictionary containing the Pet data
        """
        try:
            self.name = data["name"]
            self.category = data["category"]
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError("Invalid type for boolean [available]: " + type(data["available"]))
            self.gender = getattr(Gender, data["gender"])  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """ Returns all of the Pets in the database """
        logger.info("Processing all Pets")
        return cls.query.all()

    @classmethod
    def find(cls, pet_id: int):
        """ Finds a Pet by it's ID """
        logger.info("Processing lookup for id %s ...", pet_id)
        return cls.query.get(pet_id)

    @classmethod
    def find_or_404(cls, pet_id: int) -> list:
        """ Find a Pet by it's id """
        logger.info("Processing lookup or 404 for id %s ...", pet_id)
        return cls.query.get_or_404(pet_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Pets with the given name

        Args:
            name (string): the name of the Pets you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category: str) -> list:
        """Returns all of the Pets in a category

        Args:
            category (string): the category of the Pets you want to match
        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_availability(cls, available: bool=True) -> list:
        """Returns all Pets by their availability

        Args:
            available (boolean): True for pets that are available
        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_gender(cls, gender: Gender=Gender.Unknown) -> list:
        """Returns all Pets by their Gender

        Args:
            Gender (enum): Options are ['Male', 'Female', 'Unknown']
        """
        logger.info("Processing gender query for %s ...", gender.name)
        return cls.query.filter(cls.gender == gender)
