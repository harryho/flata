import pytest

from flata import Flata, where
from flata.middlewares import CachingMiddleware
from flata.storages import MemoryStorage, JSONStorage
# from flata.middlewares import Middleware


def test_purge(db):
    db.purge_tables()
    tb = db.table('t')
    tb.insert({})
    db.purge_tables()

    assert len(db) == 0


def test_table_all(db):
    db.purge_tables()

    tb = db.table('t')
    for i in range(10):
        tb.insert({})

    # pp(list(db.all().values()).len())
    assert len(db.all()) == 1
    assert len(tb.all()) == 10

def test_purge_table():
    table_name = 'some-other-table'
    db = Flata(storage=MemoryStorage)
    db.table(table_name)
    assert set([table_name]) == db.tables()

    db.purge_table(table_name)
    assert not set([table_name]) == db.tables()    

def test_storage_closed_once():
    class Storage(object):
        def __init__(self):
            self.closed = False

        def read(self):
            return {}

        def write(self, data):
            pass

        def close(self):
            assert not self.closed
            self.closed = True

    with Flata(storage=Storage) as db:
        db.close()

    del db
    # If db.close() is called during cleanup, the assertion will fail and throw
    # and exception    

def test_flata_memory_storage():
    with Flata('db.json', storage=MemoryStorage) as db:
        assert  isinstance( db._storage, MemoryStorage)
        db.close()

def test_flata_caching_memory_storage():
    with Flata('db.json', storage=CachingMiddleware(MemoryStorage)) as db:
        assert  isinstance( db._storage, (CachingMiddleware, MemoryStorage))
        db.close()        

def test_flata_external_cache_memory_storage():
    _cache = CachingMiddleware(MemoryStorage)()
    with Flata('db.json', cache=_cache) as db:
        assert  isinstance( db._storage, (CachingMiddleware, MemoryStorage))
        db.close()          

def test_flata_json_storage():
    with Flata('db.json', storage=JSONStorage) as db:
        assert  isinstance( db._storage, JSONStorage)
        db.close()   

def test_flata_caching_json_storage():
    with Flata('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        assert  isinstance( db._storage, (CachingMiddleware,JSONStorage))
        db.close()        
             
def test_flata_external_cache_json_storage():
    _cache = CachingMiddleware(JSONStorage)('db.json')
    with Flata('db.json', cache=_cache) as db:
        assert  isinstance( db._storage, (CachingMiddleware, JSONStorage))
        db.close()   

def test_flata_default_storage():
    with Flata('db.json', storage=JSONStorage) as db:
        assert  isinstance( db._storage, JSONStorage)
        db.close()           