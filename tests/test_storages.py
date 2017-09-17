import os
import random
import tempfile

import pytest


random.seed()

from flata import Flata, where
from flata.storages import JSONStorage, MemoryStorage, Storage

element = {'none': [None, None], 'int': 42, 'float': 3.1415899999999999,
           'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
           'dict': {'hp': 13, 'sp': 5},
           'bool': [True, False, True, False]}


def test_json(tmpdir):
    # Write contents
    path = str(tmpdir.join('test.db'))
    storage = JSONStorage(path)
    storage.write(element)

    # Verify contents
    assert element == storage.read()
    storage.close()


def test_json_kwargs(tmpdir):
    db_file = tmpdir.join('test.db.json')
    db = Flata(str(db_file), sort_keys=True, indent=4, separators=(',', ': '))

    # Create table test_table
    tb = db.table('test_table')

    # Write contents
    tb.insert({'b': 1})
    # tb.insert({'a': 1})
    print(db_file.read())

    assert db_file.read() == '''{
    "test_table": [
        {
            "b": 1,
            "id": 1
        }
    ]
}'''
    db.close()


def test_json_readwrite(tmpdir):
    """
    Regression test for issue #1
    """
    path = str(tmpdir.join('test.db.json'))

    # Create Flata instance
    db = Flata(path, storage=JSONStorage)

    # Create table test_table
    tb = db.table('test_table')

    item = {'data': 'data exists'}
    item2 = {'data': 'data not exists'}

    get = lambda s: tb.get(where('data') == s)

    tb.insert(item)
    assert dict(get('data exists'))['data'] == 'data exists'

    assert get('data not exists') is None

    tb.remove(where('data') == 'data exists')
    assert get('data exists') is None

    db.close()


def test_create_dirs():
    temp_dir = tempfile.gettempdir()
    db_dir = ''
    db_file = ''

    while True:
        dname = os.path.join(temp_dir, str(random.getrandbits(20)))
        if not os.path.exists(dname):
            db_dir = dname
            db_file = os.path.join(db_dir, 'db.json')
            break

    db_conn = JSONStorage(db_file, create_dirs=True)
    db_conn.close()

    db_exists = os.path.exists(db_file)

    os.remove(db_file)
    os.rmdir(db_dir)

    assert db_exists


def test_json_invalid_directory():
    with pytest.raises(IOError):
        with Flata('/this/is/an/invalid/path/db.json', storage=JSONStorage):
            pass


def test_in_memory():
    # Write contents
    storage = MemoryStorage()
    storage.write(element)

    # Verify contents
    assert element == storage.read()

    # Test case for #21
    other = MemoryStorage()
    other.write({})
    assert other.read() != storage.read()


def test_in_memory_close():
    with Flata('', storage=MemoryStorage) as db:
        db.table('t').insert({})


def test_custom():
    # noinspection PyAbstractClass
    class MyStorage(Storage):
        pass

    with pytest.raises(TypeError):
        MyStorage()
