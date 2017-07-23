PseuDB
----

|Build Status| 


PseuDB is inspired by TinyDB_ and lowdb_. It is a lightweight document 
oriented database optimized for PseuServer and fun :) It's written in pure
Python and has no external dependencies. The target are small apps or 
fake api that would be blown away by a SQL-DB or an external database server.

Many thanks to :
================

Markus Siemens's TinyDB. All credit should go to Markus, upon his hard work
I can create the PseuDB as what I want. I borrow some concepts from lowdb which 
will have better support for Restful API. 

Difference between TinyDB and PseuDB

- **No default table** _default table is removed in PseuDB. User needs to create a table first before inserting any data. 

_ **built-in id** PseuDB always attachs `_oid` to every record, but user can customize the unique id field for test purpose. 

- **Only table object can execute CRUD** TinyDB can execute CRUD action, but PseuDB only allow table instance to execute CRUD. This concept is borrowed from lowdb. 


- **Format of database is not compatible** Database file created by TinyDB will not be compatible with PseuDB, because data structure stored as list in PseuDB instead of dict in TinyDB. 


.. |Build Status| image:: https://travis-ci.org/harryho/pseudb.svg?branch=master
    :target: https://travis-ci.org/harryho/pseudb

.. _TinyDB: https://github.com/msiemens/tinydb
.. _lowdb: https://github.com/typicode/lowdb
