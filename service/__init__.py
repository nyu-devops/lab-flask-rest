# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Package for the application models and service routes
"""
from flask import Flask
from flask_redis import FlaskRedis
from service import config
from service.common import log_handlers

# Globally accessible libraries
# redis = FlaskRedis()


############################################################
# Initialize the Flask instance
############################################################
def init_app():
    """Initialize the core application."""
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Plugins
    # redis.init_app(app)

    with app.app_context():
        # Include our Routes

        # pylint: disable=import-outside-toplevel, unused-import
        from service import routes, models
        from service.common import error_handlers

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info("  H I T   C O U N T E R   S E R V I C E  ".center(70, "*"))
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        # Initialize the database
        try:
            app.logger.info("Initializing the Redis database")
            models.Counter.connect(app.config['DATABASE_URI'])
            app.logger.info("Connected!")
        except models.DatabaseConnectionError as err:
            app.logger.error(str(err))

        return app
