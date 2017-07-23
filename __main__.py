from pseudb import PseuDB, where
# from PseuDB.middlewares import CachingMiddleware
from pseudb.storages import MemoryStorage, JSONStorage
import os
from pprint import pprint as pp

if __name__ == '__main__':
    # element = {'none': [None, None], 'int': 42, 'float': 3.1415899999999999,
    #        'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
    #        'dict': {'hp': 13, 'sp': 5},
    #        'bool': [True, False, True, False]}
    #
    db_file = str(''.join('test.db.json'))
    #
    # # path = str(tmpdir.join('test.db'))
    # storage = JSONStorage(db_file)
    # storage.write(element)
    #
    # # Verify contents
    # assert element == storage.read()
    # storage.close()


    db = PseuDB(str(db_file), sort_keys=True, indent=4, separators=(',', ': '))
    
    # Clean up
    db.purge_tables()

    # Create table
    db.table('table').insert({'b': 1})

    # Write contents
    # db.insert({'b': 1})
    # db.insert({'a': 1})

    db.table('table_123', oid='_guid').insert({'xxx': 1})
    # db.insert({'aaaa': 1})

    pp(db.tables())
    pp(db.all())

    result = db.get('table_123').search(where('xxx')==1)
    result = db.get('table').search(where('xxx') == 1)
    pp(result)

    # assert db_file.read() == '''{
    #     "_default": {
    #         "1": {
    #             "b": 1
    #         },
    #         "2": {
    #             "a": 1
    #         }
    #     }
    # }'''
    #
    # db.close()
    #
    # # Create PseuDB instance
    # db = PseuDB(db_file, storage=JSONStorage)
    #
    # item = {'name': 'A very long entry'}
    # item2 = {'name': 'A short one'}
    #
    # get = lambda s: db.get(where('name') == s)
    #
    # db.insert(item)
    # assert get('A very long entry') == item
    #
    # db.remove(where('name') == 'A very long entry')
    # assert get('A very long entry') is None
    #
    # db.insert(item2)
    # assert get('A short one') == item2
    #
    # db.remove(where('name') == 'A short one')
    # assert get('A short one') is None
    #
    # db.close()
