import pytest

from pseudb.middlewares import CachingMiddleware
from pseudb.storages import MemoryStorage
from pseudb import PseuDB


@pytest.fixture
def db():
    db_ = PseuDB(storage=MemoryStorage)
    db_.purge_tables()
    db_.table('t').insert_multiple({'int': 1, 'char': c} for c in 'abc')
    return db_


@pytest.fixture
def storage():
    _storage = CachingMiddleware(MemoryStorage)
    return _storage()  # Initialize MemoryStorage
