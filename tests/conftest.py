import pytest

from flatdb.middlewares import CachingMiddleware
from flatdb.storages import MemoryStorage
from flatdb import FlatDB


@pytest.fixture
def db():
    db_ = FlatDB(storage=MemoryStorage)
    db_.purge_tables()
    db_.table('t').insert_multiple({'int': 1, 'char': c} for c in 'abc')
    return db_


@pytest.fixture
def storage():
    _storage = CachingMiddleware(MemoryStorage)
    return _storage()  # Initialize MemoryStorage
