"""

Flata (Version: 3.3.1)

Flata is a tiny, document oriented database optimized for your happiness :)

Flata stores differrent types of python data types using a configurable
backend. It has support for handy querying and tables.

.. codeauthor:: Harry Ho <harry.ho_long@yahoo.com>

Usage example:

>>> from flata. import Flata, where
>>> from flata.storages import MemoryStorage
>>> db = Flata(storage=MemoryStorage)
>>> tb = db.table('table1')
>>> tb.insert({'data': 0}) 
>>> tb.search(where('data') == 5)
[{'data': 5, 'id': 1}]
>>> # Now let's create a new table
>>> tbl = db.table('our_table')
>>> for i in range(10):
...     tbl.insert({'data': i})
...
>>> len(tbl.search(where('data') < 5))
5
"""

from .queries import Query, where
from .storages import Storage, JSONStorage, MemoryStorage
from .middlewares import Middleware, CachingMiddleware
from .database import Flata

__all__ = ('Flata', 'Storage', 'JSONStorage', 'MemoryStorage', 'Middleware', 'CachingMiddleware', 'Query', 'where')


