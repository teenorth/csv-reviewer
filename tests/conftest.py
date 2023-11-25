import pytest
from api import Api
import json
import os


@pytest.fixture(scope='session')
def data():
    yield {}
