import pytest

from flata import Flata, where
from flata.storages import MemoryStorage
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