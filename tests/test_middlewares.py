import os

from flata import Flata
from flata.middlewares import CachingMiddleware
from flata.storages import MemoryStorage, JSONStorage

if 'xrange' not in dir(__builtins__):
    # noinspection PyShadowingBuiltins
    xrange = range  # Python 3 support


element = {'none': [None, None], 'int': 42, 'float': 3.1415899999999999,
           'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
           'dict': {'hp': 13, 'sp': 5},
           'bool': [True, False, True, False]}


def test_caching(storage):
    # Write contents
    storage.write(element)

    # Verify contents
    assert element == storage.read()


def test_caching_read():
    db = Flata(storage=CachingMiddleware(MemoryStorage))
    assert not db.all()


def test_caching_write_many(storage):
    storage.WRITE_CACHE_SIZE = 3

    # Storage should be still empty
    assert storage.memory is None

    # Write contents
    for x in xrange(2):
        storage.write(element)
        assert storage.memory is None  # Still cached

    storage.write(element)

    # Verify contents: Cache should be emptied and written to storage
    assert storage.memory


def test_caching_flush(storage):
    # Write contents
    storage.write(element)

    storage.flush()

    # Verify contents: Cache should be emptied and written to storage
    assert storage.memory


def test_caching_write(storage):
    # Write contents
    storage.write(element)

    storage.close()

    # Verify contents: Cache should be emptied and written to storage
    assert storage.storage.memory


def test_nested():
    storage = CachingMiddleware(MemoryStorage)
    storage()  # Initialization

    # Write contents
    storage.write(element)

    # Verify contents
    assert element == storage.read()


def test_caching_json_write(tmpdir):
    path = str(tmpdir.join('test.db'))

    with Flata(path, storage=CachingMiddleware(JSONStorage)) as db:
        db.table('t').insert({'key': 'value'})

    # Verify database filesize
    statinfo = os.stat(path)
    assert statinfo.st_size != 0

    # Assert JSON file has been closed
    assert db._storage._handle.closed

    del db

    # Repoen database
    with Flata(path, storage=CachingMiddleware(JSONStorage)) as db:
        assert db.table('t').all() == [{'id':1, 'key': 'value'}]
