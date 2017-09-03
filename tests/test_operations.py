from flata import where
from flata.operations import delete, increment, decrement


def test_delete(db):
    db.table('t').update(delete('int'), where('char') == 'a')
    assert 'int' not in db.table('t').get(where('char') == 'a')


def test_increment(db):
    db.table('t').update(increment('int'), where('char') == 'a')
    assert db.table('t').get(where('char') == 'a')['int'] == 2


def test_decrement(db):
    db.table('t').update(decrement('int'), where('char') == 'a')
    assert db.table('t').get(where('char') == 'a')['int'] == 0
