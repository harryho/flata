"""
Contains the :class:`database <pseudb.database.PseuDB>` and
:class:`tables <pseudb.database.Table>` implementation.
"""
from . import JSONStorage
from .utils import LRUCache, iteritems, itervalues


class Element(dict):
    """
    Represents an element stored in the database.

    This is a transparent proxy for database elements. It exists
    to provide a way to access an element's id via ``el.oid``.
    """
    def __init__(self, value=None, oid=None, **kwargs):
        super(Element, self).__init__(**kwargs)

        if value is not None:
            self.update(value)
            self.oid = oid


class StorageProxy(object):

    DEFAULT_OID_FIELD = '_oid'

    def __init__(self, storage, table_name, **kwargs):
        self._storage = storage
        self._table_name = table_name
        self._oid = kwargs.pop('oid', StorageProxy.DEFAULT_OID_FIELD)

    def read(self):
        try:
            raw_data = (self._storage.read() or {})[self._table_name]
        except KeyError:
            self.write({})
            return {}

        data = {}
        # for key, val in iteritems(raw_data):
        #     oid = int(key)
        #     data[oid] = Element(val, oid)

        for item in raw_data:
             oid = item[self._oid]
             data[oid] = Element(item, oid)

        return data

    def write(self, values):
        data = self._storage.read() or {}
        data[self._table_name] = values
        self._storage.write(data)

    def purge_table(self):
        try:
            data = self._storage.read() or {}
            del data[self._table_name]
            self._storage.write(data)
        except KeyError:
            pass

    @property
    def table_name(self):
        return self._table_name

    @property
    def oid(self):
        return self._oid or StorageProxy.DEFAULT_OID_FIELD



class PseuDB(object):
    """
    The main class of PseuDB.

    Gives access to the database, provides methods to create/delete/search
    and getting tables.

    PseuDB is different from TinyDB, which can not access and manipulate 
    data on the table from the instance of PseudB.

    There is no default in PseuDB as well.
    """

    DEFAULT_STORAGE = JSONStorage

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of PseuDB.

        All arguments and keyword arguments will be passed to the underlying
        storage class (default: :class:`~pseudb.storages.JSONStorage`).

        :param storage: The class of the storage to use. Will be initialized
                        with ``args`` and ``kwargs``.
        """

        storage = kwargs.pop('storage', PseuDB.DEFAULT_STORAGE)
        # table = kwargs.pop('default_table', PseuDB.DEFAULT_TABLE)

        # Prepare the storage
        self._opened = False

        #: :type: Storage
        self._storage = storage(*args, **kwargs)

        self._opened = True

        # Prepare the default table

        self._tables = {}
        self._table = None # self.table(table)

    def table(self, name, **options):
        """
        Get access to a specific table.

        Creates a new table, if it hasn't been created before, otherwise it
        returns the cached :class:`~pseudb.Table` object.

        :param name: The name of the table. It is a required input.
        :type name: str
        :param oid: Customize the object id field.
        :param cache_size: How many query results to cache.

        """

        if not name:
            raise ValueError('Table name can not be None or empty.')

        if name in self._tables:
            return self._tables[name]

        table = self.table_class(StorageProxy(self._storage, name, **options), **options)

        self._tables[name] = table
        self._table = table

        # table._read will create an empty table in the storage, if necessary
        table._read()

        return table

    def get(self, name):
        try:
            return self._tables[name]
        except KeyError:
            return None


    def tables(self):
        """
        Get the names of all tables in the database.

        :returns: a set of table names
        :rtype: set[str]
        """

        return set(self._storage.read())

    def all(self):
        """
        Get all elements stored in the table.

        :returns: a list with all elements.
        :rtype: list[Element]
        """

        return  self._storage.read()

    def purge_tables(self):
        """
        Purge all tables from the database. **CANNOT BE REVERSED!**
        """

        self._storage.write({})
        self._tables.clear()

    def purge_table(self, name):
        """
        Purge a specific table from the database. **CANNOT BE REVERSED!**

        :param name: The name of the table.
        :type name: str
        """
        if name in self._tables:
            del self._tables[name]

        proxy = StorageProxy(self._storage, name)
        proxy.purge_table()

    def close(self):
        """
        Close the database.
        """
        self._opened = False
        self._storage.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._opened is True:
            self.close()

    # def __getattr__(self, name):
    #     """
    #     Forward all unknown attribute calls to the underlying standard table.
    #     """
    #     return getattr(self._table, name)

    # Methods that are executed on the default table
    # Because magic methods are not handlet by __getattr__ we need to forward
    # them manually here

    def __len__(self):
        """
        Get the total number of elements in the default table.

        >>> db = PseuDB('db.json')
        >>> len(db)
        0
        """
        return len(self._table)

    def __iter__(self):
        """
        Iter over all elements from default table.
        """
        return self._table.__iter__()



class Table(object):
    """
    Represents a single PseuDB Table.
    """

    def __init__(self, storage, cache_size=10, oid=StorageProxy.DEFAULT_OID_FIELD):
        """
        Get access to a table.

        :param storage: Access to the storage
        :type storage: StorageProxyus
        :param cache_size: Maximum size of query cache.
        """

        self._storage = storage
        self._table_name = storage.table_name
        self._oid = storage.oid
        self._query_cache = LRUCache(capacity=cache_size)

        data = self._read()
        if data:
            self._last_id = max(i for i in data)
        else:
            self._last_id = 0

    def process_elements(self, func, cond=None, oids=None):
        """
        Helper function for processing all elements specified by condition
        or IDs.

        A repeating pattern in PseuDB is to run some code on all elements
        that match a condition or are specified by their ID. This is
        implemented in this function.
        The function passed as ``func`` has to be a callable. It's first
        argument will be the data currently in the database. It's second
        argument is the element ID of the currently processed element.

        See: :meth:`~.update`, :meth:`.remove`

        :param func: the function to execute on every included element.
                     first argument: all data
                     second argument: the current oid
        :param cond: elements to use, or
        :param oids: elements to use
        :returns: the element IDs that were affected during processed
        """

        data = self._read()
        updated_data = []

        if oids is not None:
            # Processed element specified by id
            for oid in oids:
                func(data, oid)
                if oid in data:
                    updated_data.append(data[oid])

        else:
            # Collect affected oids
            oids = []

            # Processed elements specified by condition
            for oid in list(data):
                if cond(data[oid]):
                    func(data, oid)
                    oids.append(oid)
                    if oid in data:
                        updated_data.append(data[oid])

        
        new_data = list(data.values())

        self._write(new_data)

        return oids, updated_data

    def clear_cache(self):
        """
        Clear the query cache.

        A simple helper that clears the internal query cache.
        """
        self._query_cache.clear()

    def _get_next_id(self):
        """
        Increment the ID used the last time and return it
        """

        current_id = self._last_id + 1
        self._last_id = current_id

        return current_id

    def _read(self):
        """
        Reading access to the DB.

        :returns: all values
        :rtype: dict
        """

        return self._storage.read()

    def _write(self, values):
        """
        Writing access to the DB.

        :param values: the new values to write
        :type values: dict
        """

        self._query_cache.clear()
        self._storage.write(values)

    def __len__(self):
        """
        Get the total number of elements in the table.
        """
        return len(self._read())

    def all(self):
        """
        Get all elements stored in the table.

        :returns: a list with all elements.
        :rtype: list[Element]
        """

        return  list(itervalues(self._read()))

    def __iter__(self):
        """
        Iter over all elements stored in the table.

        :returns: an iterator over all elements.
        :rtype: listiterator[Element]
        """

        for value in itervalues(self._read()):
            yield value

    def insert(self, element):
        """
        Insert a new element into the table.

        :param element: the element to insert
        :returns: the inserted element with ID
        """

        if not isinstance(self, Table):
            raise ValueError('Only table instance can support insert action.')

        oid = self._get_next_id()

        if not isinstance(element, dict):
            raise ValueError('Element is not a dictionary')

        data = self._read()

        items = list(data.values())
        element[self._oid] = oid
        items.append(element)

        self._write(items)

        return element

    def insert_multiple(self, elements):
        """
        Insert multiple elements into the table.

        :param elements: a list of elements to insert
        :returns: a list containing the inserted elements with IDs
        """
        if not isinstance(self, Table):
            raise ValueError('Only table instance can support insert action.')

        oids = []
        data = self._read()
        items = list(data.values())

        for element in elements:
            oid = self._get_next_id()
            oids.append(oid)
            element[self._oid] = oid
            items.append(element)

            # data[oid] = element

        self._write(items)

        return elements

    def remove(self, cond=None, oids=None):
        """
        Remove all matching elements.

        :param cond: the condition to check against
        :type cond: query
        :param oids: a list of element IDs
        :type oids: list
        :returns: a list containing the removed element's ID
        """

        return self.process_elements(lambda data, oid: data.pop(oid),
                                     cond, oids)

    def update(self, fields, cond=None, oids=None):
        """
        Update all matching elements to have a given set of fields.

        :param fields: the fields that the matching elements will have
                       or a method that will update the elements
        :type fields: dict | dict -> None
        :param cond: which elements to update
        :type cond: query
        :param oids: a list of element IDs
        :type oids: list
        :returns: a list containing the updated element's ID
        """

        if callable(fields):
            return self.process_elements(
                lambda data, oid: fields(data[oid]),
                cond, oids
            )
        else:
            return self.process_elements(
                lambda data, oid: data[oid].update(fields),
                cond, oids
            )

    def purge(self):
        """
        Purge the table by removing all elements.
        """

        self._write({})
        self._last_id = 0

    def search(self, cond):
        """
        Search for all elements matching a 'where' cond.

        :param cond: the condition to check against
        :type cond: Query

        :returns: list of matching elements
        :rtype: list[Element]
        """

        if cond in self._query_cache:
            return self._query_cache[cond][:]

        elements = [element for element in self.all() if cond(element)]
        self._query_cache[cond] = elements

        return elements[:]

    def get(self, cond=None, oid=None):
        """
        Get exactly one element specified by a query or and ID.

        Returns ``None`` if the element doesn't exist

        :param cond: the condition to check against
        :type cond: Query

        :param oid: the element's ID

        :returns: the element or None
        :rtype: Element | None
        """

        # Cannot use process_elements here because we want to return a
        # specific element

        if oid is not None:
            # Element specified by ID
            return self._read().get(oid, None)

        # Element specified by condition
        for element in self.all():
            if cond(element):
                return element

    def count(self, cond):
        """
        Count the elements matching a condition.

        :param cond: the condition use
        :type cond: Query
        """

        return len(self.search(cond))

    def contains(self, cond=None, oids=None):
        """
        Check wether the database contains an element matching a condition or
        an ID.

        If ``oids`` is set, it checks if the db contains an element with one
        of the specified.

        :param cond: the condition use
        :type cond: Query
        :param oids: the element IDs to look for
        """

        if oids is not None:
            # Elements specified by ID
            return any(self.get(oid=oid) for oid in oids)

        # Element specified by condition
        return self.get(cond) is not None

# Set the default table class
PseuDB.table_class = Table
