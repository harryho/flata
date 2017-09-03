import pytest

from flata.middlewares import CachingMiddleware
from flata.storages import MemoryStorage
from flata import Flata


@pytest.fixture
def db():
    db_ = Flata(storage=MemoryStorage)
    db_.purge_tables()
    db_.table('t').insert_multiple({'int': 1, 'char': c} for c in 'abc')
    return db_


@pytest.fixture
def storage():
    _storage = CachingMiddleware(MemoryStorage)
    return _storage()  # Initialize MemoryStorage
