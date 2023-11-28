from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from api.config import Config
import logging
import os
import importlib
from flask_bcrypt import Bcrypt
from api.errors import handle_api_exception, ApiExceptionBase

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


class Api:
    """Singleton instance, initializing all required configurations for the
    API. Providing assessors for each configuration. Can easily be used
    everywhere in the application.
    """

    _instance = None
    _app = None
    _client = None
    _db = None
    _bcrypt = None
    _cors = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls.__new__(cls)
            cls._instance.__init_flask()
            cls._instance.__init_cors()
            cls._instance.__init_mongo()
            cls._instance.__init_bcrypt()
        return cls._instance

    def __init_flask(self):
        self._app = Flask(__name__)
        self._app.config.from_object(Config)

        self._app.wsgi_app = DispatcherMiddleware(
            Response("Route not found", status=404), {"/api/1.0": self._app.wsgi_app}
        )

        self._app.url_map.strict_slashes = False

        self._app.register_error_handler(ApiExceptionBase, handle_api_exception)

        self.__import_routes_from_directory()

    def __init_cors(self):
        self._cors = CORS(
            self.app(), resources={r"/*": {"origins": self.config("ALLOWED_ORIGINS")}}
        )

    def __init_mongo(self):
        self._client = MongoClient(self.config("DB_URL"))
        self._db = self._client["csv-reviewer"]

    def __init_bcrypt(self):
        self._bcrypt = Bcrypt()
        self._bcrypt.init_app(self.app())

    def __import_routes_from_directory(self, directory="api"):
        for root, dirs, files in os.walk(directory):
            if "routes.py" in files:
                module_path = root.replace("/", ".").replace("\\", ".") + ".routes"
                module = importlib.import_module(module_path)
                blueprint = root.split(os.path.sep)[-1]
                if hasattr(module, blueprint):
                    self._app.register_blueprint(getattr(module, blueprint))

    @classmethod
    def app(cls):
        return cls.instance()._app

    @classmethod
    def config(cls, key):
        return cls.instance()._app.config.get(key)

    @classmethod
    def db(cls):
        return cls.instance()._db

    @classmethod
    def client(cls):
        return cls.instance()._client

    @classmethod
    def collection(cls, collection):
        return cls.instance()._db[collection]

    @classmethod
    def bcrypt(cls):
        return cls.instance()._bcrypt
