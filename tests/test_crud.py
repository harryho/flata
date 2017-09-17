# coding=utf-8
import sys

import pytest

from flata import Flata, where, Query
from flata.storages import MemoryStorage
from flata.middlewares import Middleware, CachingMiddleware

def test_insert(db):
    db.purge_tables()
    tb = db.table('t')
    tb.insert({'int': 1, 'char': 'a'})

    assert tb.count(where('int') == 1) == 1

    db.purge_tables()
 
    db.table('t').insert({'int': 1, 'char': 'a'})
    db.table('t').insert({'int': 1, 'char': 'b'})
    db.table('t').insert({'int': 1, 'char': 'c'})

    assert db.table('t').count(where('int') == 1) == 3
    assert db.table('t').count(where('char') == 'a') == 1


def test_insert_ids(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 1, 'char': 'a', 'int': 1}
    assert db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 2, 'char': 'a', 'int': 1}


def test_insert_multiple(db):
    db.purge_tables()

    # Insert multiple from list
    db.table('t').insert_multiple([{'int': 1, 'char': 'a'},
                        {'int': 1, 'char': 'b'},
                        {'int': 1, 'char': 'c'}])

    assert db.table('t').count(where('int') == 1) == 3
    assert db.table('t').count(where('char') == 'a') == 1

    # Insert multiple from generator function
    def generator():
        for j in range(10):
            yield {'int': j}

    db.purge_tables()

    db.table('t').insert_multiple(generator())

    for i in range(10):
        assert db.table('t').count(where('int') == i) == 1
    assert db.table('t').count(where('int').exists()) == 10

    # Insert multiple from inline generator
    db.purge_tables()

    db.table('t').insert_multiple({'int': i} for i in range(10))

    for i in range(10):
        assert db.table('t').count(where('int') == i) == 1


def test_insert_multiple_with_ids(db):
    db.purge_tables()

    # Insert multiple from list
    assert db.table('t').insert_multiple(
        [{'int': 1, 'char': 'a'},
        {'int': 1, 'char': 'b'},
        {'int': 1, 'char': 'c'}]) == [{'id': 1, 'char': 'a', 'int': 1},
                                     {'id': 2, 'char': 'b', 'int': 1}, 
                                     {'id': 3, 'char': 'c', 'int': 1}]


def test_remove(db):
    db.table('t').remove(where('char') == 'b')
    assert len(db.table('t').all()) == 2
    assert db.table('t').count(where('int') == 1) == 2

def test_remove_by_id(db):
    db.table('t').remove(where('id') == 1)
    assert len(db.table('t').all()) == 2
    db.table('t').remove( ids = [2] )
    assert len(db.table('t').all()) == 1  


def test_remove_multiple(db):
    db.table('t').remove(where('int') == 1)

    assert len(db.table('t').all()) == 0


def test_remove_ids(db):
    db.table('t').remove(ids=[1, 2])

    assert len(db.table('t').all()) == 1


def test_remove_returns_ids(db):
    assert db.table('t').remove(where('char') == 'b')[0] == [2]


def test_update(db):
    assert db.table('t').count(where('int') == 1) == 3

    db.table('t').update({'int': 2}, where('char') == 'a')

    assert db.table('t').count(where('int') == 2) == 1
    assert db.table('t').count(where('int') == 1) == 2


def test_update_returns_ids(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 1, 'char': 'a', 'int': 1}
    assert db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 2, 'char': 'a', 'int': 1}

    assert db.table('t').update(
        {'char': 'b'}, where('int') == 1) == ( 
            [1, 2], [{'id': 1, 'char': 'b', 'int': 1},
                {'id': 2, 'char': 'b', 'int': 1}])


def test_update_transform(db):
    def increment(field):
        def transform(el):
            el[field] += 1

        return transform

    def delete(field):
        def transform(el):
            del el[field]

        return transform

    assert db.table('t').count(where('int') == 1) == 3

    db.table('t').update(increment('int'), where('char') == 'a')
    db.table('t').update(delete('char'), where('char') == 'a')

    assert db.table('t').count(where('int') == 2) == 1
    assert db.table('t').count(where('char') == 'a') == 0
    assert db.table('t').count(where('int') == 1) == 2


def test_update_ids(db):
    db.table('t').update({'int': 2}, ids=[1, 2])

    assert db.table('t').count(where('int') == 2) == 2


def test_queries_where(db):
    assert len(db.table('t').all() ) == 3
    assert not db.table('t')._query_cache
    assert len(db.table('t').search(where('int') == 1)) == 3

    assert len(db.table('t')._query_cache) == 1
    assert len(db.table('t').search(where('int') == 1)) == 3  # Query result from cache
    assert len(db.table('t').search(~(where('char')=='a'))) == 2
    assert len(db.table('t').search((where('int') == 1) & (where('char')=='a'))) == 1
    assert len(db.table('t').search((where('char')=='b') |  (where('char')=='a'))) == 2

def test_queries_query(db):
    assert len(db.table('t').search(Query().char == 'a')) == 1
    assert len(db.table('t').search(Query().char == 'b')) == 1
    assert len(db.table('t').search((Query().char == 'c') & (Query().int == 1 ))) == 1
    assert len(db.table('t').search((Query().char == 'c') | (Query().char == 'a' ))) == 2
    assert len(db.table('t').search((Query()['char'] == 'c') & (Query()['int'] == 1 ))) == 1
    assert len(db.table('t').search((Query()['char']== 'c') | (Query()['char'] == 'a' ))) == 2


def test_queries_matches(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}

    assert len(db.table('t').search(Query()['chars'].matches('abcd'))) == 1
    assert len(db.table('t').search(Query()['chars'].matches('abc'))) == 1
    assert len(db.table('t').search(Query()['chars'].matches('ad'))) == 0
    # assert len(db.table('t').search(Query()['chars'].match(['cd']))) == 1

def test_queries_matches_ignore_case(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}

    assert len(db.table('t').search(Query()['chars'].matches_ignore_case('aBcd'))) == 1
    assert len(db.table('t').search(Query()['chars'].matches_ignore_case('abcc'))) == 0
    assert len(db.table('t').search(Query()['chars'].matches_ignore_case('Ab'))) == 1

def test_queries_search(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}

    assert len(db.table('t').search(Query()['chars'].search('cd'))) == 1
    assert len(db.table('t').search(Query()['chars'].search('d'))) == 1
    assert len(db.table('t').search(Query()['chars'].search('a'))) == 2
    assert len(db.table('t').search(Query()['chars'].search('abcd'))) == 1
    assert len(db.table('t').search(Query()['chars'].search('bcda'))) == 0

def test_queries_search_ignore_case(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}

    assert len(db.table('t').search(Query()['chars'].search_ignore_case('Cd'))) == 1
    assert len(db.table('t').search(Query()['chars'].search_ignore_case('D'))) == 1
    assert len(db.table('t').search(Query()['chars'].search_ignore_case('a'))) == 2
    assert len(db.table('t').search(Query()['chars'].search_ignore_case('aBcd'))) == 1
    assert len(db.table('t').search(Query()['chars'].search_ignore_case('bcda'))) == 0


@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="requires python3")
def test_queries_any(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}
    assert db.table('t').insert({'int': 3, 'chars': 'x', 'char2': 'abcd'}) == {'id': 3, 'chars': 'x', 'char2': 'abcd', 'int': 3}

    assert len(db.table('t').search(Query()['chars'].any(['d']))) == 1
    assert len(db.table('t').search(Query()['chars'].any(['c']))) == 2
    assert len(db.table('t').search(Query()['chars'].any(['acd']))) == 0
    assert len(db.table('t').search(Query()['chars'].any('acd'))) == 2

def test_queries_any_in_list(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'charList': ['abcd', 'a']}) == {'id': 1, 'charList': ['abcd', 'a'], 'int': 1}
    assert db.table('t').insert({'int': 2, 'charList': ['ac']}) == {'id': 2, 'charList': ['ac'], 'int': 2}

    assert len(db.table('t').search(Query()['charList'].any(['a']))) == 1
    assert len(db.table('t').search(Query()['charList'].any(['a', 'abcd']))) == 1
    assert len(db.table('t').search(Query()['charList'].any('ac'))) == 2
    assert len(db.table('t').search(Query()['charList'].any('abcd'))) == 1

@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="requires python3")
def test_queries_all(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'chars': 'abcd'}) == {'id': 1, 'chars': 'abcd', 'int': 1}
    assert db.table('t').insert({'int': 2, 'chars': 'ac'}) == {'id': 2, 'chars': 'ac', 'int': 2}
    assert db.table('t').insert({'int': 3, 'chars': 'x', 'char2': 'abcd'}) == {'id': 3, 'chars': 'x', 'char2': 'abcd', 'int': 3}

    assert len(db.table('t').search(Query()['chars'].all(['d']))) == 1
    assert len(db.table('t').search(Query()['chars'].all(['c']))) == 2
    assert len(db.table('t').search(Query()['chars'].all(['acd']))) == 0
    assert len(db.table('t').search(Query()['chars'].all('acd'))) == 1


def test_queries_all_in_list(db):
    db.purge_tables()
    assert db.table('t').insert({'int': 1, 'charList': ['abcd', 'a']}) == {'id': 1, 'charList': ['abcd', 'a'], 'int': 1}
    assert db.table('t').insert({'int': 2, 'charList': ['ac']}) == {'id': 2, 'charList': ['ac'], 'int': 2}

    assert len(db.table('t').search(Query()['charList'].all(['abcd']))) == 1
    assert len(db.table('t').search(Query()['charList'].all(['a']))) == 1
    assert len(db.table('t').search(Query()['charList'].all(['ac']))) == 1
    assert len(db.table('t').search(Query()['charList'].all('abcd'))) == 0
    assert len(db.table('t').search(Query()['charList'].all('ac'))) == 0

def test_get(db):
    item = db.table('t').get(where('char') == 'b')
    assert item['char'] == 'b'


def test_get_ids(db):
    el = db.table('t').all()[0]
    assert db.table('t').get(id=el.id) == el
    assert db.table('t').get(id=float('NaN')) is None


def test_count(db):
    assert db.table('t').count(where('int') == 1) == 3
    assert db.table('t').count(where('char') == 'd') == 0


def test_contains(db):
    assert db.table('t').contains(where('int') == 1)
    assert not db.table('t').contains(where('int') == 0)


def test_contains_ids(db):
    assert db.table('t').contains(ids=[1, 2])
    assert not db.table('t').contains(ids=[88])


def test_get_idempotent(db):
    u = db.table('t').get(where('int') == 1)
    z = db.table('t').get(where('int') == 1)
    assert u == z


def test_multiple_dbs():
    db1 = Flata(storage=MemoryStorage)
    db2 = Flata(storage=MemoryStorage)

    db1.table('t').insert({'int': 1, 'char': 'a'})
    db1.table('t').insert({'int': 1, 'char': 'b'})
    db1.table('t').insert({'int': 1, 'value': 5.0})

    db2.table('t').insert({'color': 'blue', 'animal': 'turtle'})

    assert len(db1.table('t').all()) == 3
    assert len(db2.table('t').all()) == 1



def test_unique_ids(tmpdir):
    """
    :type tmpdir: py._path.local.LocalPath
    """
    path = str(tmpdir.join('test.db.json'))

    # Verify ids are unique when reopening the DB and inserting
    with Flata(path) as _db:
        _db.table('t').insert({'x': 1})

    with Flata(path) as _db:
        _db.table('t').insert({'x': 1})

    with Flata(path) as _db:
        data = _db.table('t').all()

        assert data[0].id != data[1].id

    # Verify ids stay unique when inserting/removing
    with Flata(path) as _db:
        _db.purge_tables()
        _db.table('t').insert_multiple({'x': i} for i in range(5))
        _db.table('t').remove(where('x') == 2)

        assert len(_db.table('t').all()) == 4

        ids = [e.id for e in _db.table('t').all()]
        assert len(ids) == len(set(ids))


def test_lastid_after_open(tmpdir):
    NUM = 100
    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        _db.table('t').insert_multiple({'i': i} for i in range(NUM))

    with Flata(path) as _db:
        assert _db.table('t')._last_id == NUM


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="requires python2")
def test_unicode_memory(db):
    unic_str = 'ß'.decode('utf-8')
    byte_str = 'ß'

    db.table('t').insert({'value': unic_str})
    assert db.table('t').contains(where('value') == byte_str)
    assert db.table('t').contains(where('value') == unic_str)

    db.purge_tables()
    db.table('t').insert({'value': byte_str})
    assert db.table('t').contains(where('value') == byte_str)
    assert db.table('t').contains(where('value') == unic_str)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="requires python2")
def test_unicode_json(tmpdir):
    unic_str1 = 'a'.decode('utf-8')
    byte_str1 = 'a'

    unic_str2 = 'ß'.decode('utf-8')
    byte_str2 = 'ß'

    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        _db.purge_tables()
        _db.table('t').insert({'value': byte_str1})
        _db.table('t').insert({'value': byte_str2})
        assert _db.table('t').contains(where('value') == byte_str1)
        assert _db.table('t').contains(where('value') == unic_str1)
        assert _db.table('t').contains(where('value') == byte_str2)
        assert _db.table('t').contains(where('value') == unic_str2)

    with Flata(path) as _db:
        _db.purge_tables()
        _db.table('t').insert({'value': unic_str1})
        _db.table('t').insert({'value': unic_str2})
        assert _db.table('t').contains(where('value') == byte_str1)
        assert _db.table('t').contains(where('value') == unic_str1)
        assert _db.table('t').contains(where('value') == byte_str2)
        assert _db.table('t').contains(where('value') == unic_str2)


def testids_json(tmpdir):
    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        _db.purge_tables()
        assert _db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 1, 'char': 'a', 'int': 1}
        assert _db.table('t').insert({'int': 1, 'char': 'a'}) == {'id': 2, 'char': 'a', 'int': 1}

        _db.purge_tables()
        assert _db.table('t').insert_multiple(
            [{'int': 1, 'char': 'a'}
            ,{'int': 1, 'char': 'b'}
            ,{'int': 1, 'char': 'c'}]) == [{'id': 1, 'char': 'a', 'int': 1}
                                            ,{'id': 2, 'char': 'b', 'int': 1}
                                            ,{'id': 3, 'char': 'c', 'int': 1}]

        assert _db.table('t').contains(ids=[1, 2])
        assert not _db.table('t').contains(ids=[88])

        _db.table('t').update({'int': 2}, ids=[1, 2])
        assert _db.table('t').count(where('int') == 2) == 2

        el = _db.table('t').all()[0]
        assert _db.table('t').get(id=el.id) == el
        assert _db.table('t').get(id=float('NaN')) is None

        _db.table('t').remove(ids=[1, 2])
        assert len(_db.table('t').all()) == 1



def test_insert_object(tmpdir):
    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        _db.purge_tables()
        data = [ {'int': 1, 'object' : {'object_id': 2}}]
        _db.table('t').insert_multiple(data)

        assert _db.table('t').all() == [{'id': 1, 'int': 1, 'object': {'object_id': 2}}]

def test_insert_invalid_array_string(tmpdir):
    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        data = [{'int': 1}, {'int': 2}]
        _db.table('t').insert_multiple(data)

        with pytest.raises(ValueError):
            _db.table('t').insert([1, 2, 3])  # Fails

        with pytest.raises(ValueError):
            _db.table('t').insert('fails')  # Fails

        assert len(_db.table('t').all()) == 2

        # _db.table('t').insert({'int': 3})  # Does not fail


def test_insert_invalid_dict(tmpdir):
    path = str(tmpdir.join('test.db.json'))

    with Flata(path) as _db:
        _db.purge_tables()
        data = [{'int': 1}, {'int': 2}]
        _db.table('t').insert_multiple(data)

        with pytest.raises(TypeError):
            _db.table('t').insert({'int': set(['bark'])})  # Fails

        assert len(_db.table('t').all()) == 2 #  Table only has 2 records

        # _db.table('t').insert({'int': 3})  # Does not fail


def test_gc(tmpdir):
    path = str(tmpdir.join('test.db.json'))
    db = Flata(path)
    table = db.table('foo')
    table.insert({'something': 'else'})
    table.insert({'int': 13})
    assert len(table.search(where('int') == 13)) == 1
    assert table.all() == [{'id': 1,'something': 'else'}, {'id': 2,'int': 13}]
    db.close()


def test_empty_write(tmpdir):
    path = str(tmpdir.join('test.db.json'))

    class ReadOnlyMiddleware(Middleware):
        def write(self, data):
            raise AssertionError('No write for unchanged db')

    Flata(path).close()
    Flata(path, storage=ReadOnlyMiddleware()).close()


def test_not_defaultid (tmpdir):
    path = str(tmpdir.join('test.db.json'))
    db = Flata(path)
    table = db.table('foo', id_field='_not_default_id')
    table.insert({'something': 'else'})
    assert table.all() == [{'_not_default_id': 1,'something': 'else'}]

def test_update_with_not_default_id(tmpdir):
    path = str(tmpdir.join('test.db.json'))
    db = Flata(path)
    table = db.table('foo', id_field='_not_default_id')
    table.insert({'something': 'else'})

    assert db.table('foo').count(where('something') == 'else') == 1

    db.table('foo').update({'something': 'updated'}, where('something') == 'else')

    assert db.table('foo').count(where('something') == 'updated') == 1
    # assert db.table('t').count(where('int') == 1) == 2  

def test_remove_with_not_default_id(tmpdir):
    path = str(tmpdir.join('test.db.json'))
    db = Flata(path)
    table = db.table('foo', id_field='_not_default_id')
    table.insert({'something': 'else'})

    assert db.table('foo').count(where('something') == 'else') == 1

    db.table('foo').remove(where('something') == 'else')

    assert db.table('foo').all() == []

def test_query_memory_storage():
    db = Flata(storage=MemoryStorage)
    db.table('t').insert_multiple([
        {'name': 'foo', 'value': 42},
        {'name': 'bar', 'value': -1337}
    ])

    query = where('value') > 0

    results = db.table('t').search(query)
    assert len(results) == 1
    # Now, modify the result ist
    results.extend([1])

    assert db.table('t').search(query) == [{'id': 1,'name': 'foo', 'value': 42}]



def test_insert_with_external_cache(db):
    _cache = CachingMiddleware(MemoryStorage)()
    db = Flata(cache=_cache)
    tb = db.table('t')
    tb.insert({'int': 1, 'char': 'a'})

    assert tb.count(where('int') == 1) == 1

    db2 = Flata(cache=_cache)
    tb = db2.table('t')
 
    db2.table('t').insert({'int': 1, 'char': 'a'})
    db2.table('t').insert({'int': 1, 'char': 'b'})
    db2.table('t').insert({'int': 1, 'char': 'c'})

    assert db2.table('t').count(where('int') == 1) == 4
    assert db2.table('t').count(where('char') == 'a') == 2

def test_remove_with_external_cache(db):
    _cache = CachingMiddleware(MemoryStorage)()
    db = Flata(cache=_cache)
    tb = db.table('t')
    tb.insert({'int': 1, 'char': 'a'})

    assert tb.count(where('int') == 1) == 1

    db2 = Flata(cache=_cache)
    tb = db2.table('t')
 
    db2.table('t').remove(where('int') == 1)
    assert db2.table('t').count(where('int') == 1) == 0

def test_update_with_external_cache(db):
    _cache = CachingMiddleware(MemoryStorage)()
    db = Flata(cache=_cache)
    tb = db.table('t')
    tb.insert({'int': 1, 'char': 'a'})

    assert tb.count(where('int') == 1) == 1
    
    db2 = Flata(cache=_cache)
    tb = db2.table('t')
    db2.table('t').update({'int': 2}, where('char') == 'a')

    assert db2.table('t').count(where('int') == 2) == 1

def test_flatdb_is_iterable(db):
    assert [r for r in db] == db.table('t').all()


