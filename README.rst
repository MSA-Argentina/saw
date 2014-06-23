SAW / Trying to make SQLAlchemy more easy 
=========================================

About me:
---------

This is a library that tries to make SQLAlchemy usage more easy. SQLAlchemy
gives you a lot of different ways to acomplish what you want to do, and
SAW tryies to give you 'one common and easy way to do a specific task' 
without interfering if you need to use all the power of SQLAlchemy. 

My documentation is a doctest:
------------------------------

Before executing the doctest, be sure to have created a virtualenv and
installed my requirements.txt. Also to install me (python ./setup.py develop).
You can excecute me as a doctest using the script: *rundoctest* .
For example:
    (bash)(saw)$: ./rundoctest


Introduction to saw, configuring the database and declaring a model:
--------------------------------------------------------------------

Generally, (when using me) you'll be defining two things to work with 
databases:
    * Database settings like what engine are you using (postgresql, oracle,
      mysql, whatever), port, user, password, blah, blah, etc ...
    * Your database model, as model we mean Table definitions, their
      Columns, Relatinos, types, blah, blah, etc.

Let's go with the first thing, define the database settings, we are going 
to use a sqlite db in memory:

    >>> import saw 
    >>> db = saw.DB(name='doctest', engine='sqlite', in_memory=True)

Our db doesnt have any tables, yet.

    >>> assert len(db.tables) == 0

Lets define a Human Person model object that will be respresented as a Table
in the database:

    >>> 'Person' in db.tables
    False

    >>> class Person(db.Model):
    ...     """ A Human Person."""
    ...     __tablename__ = u'Person' 
    ...
    ...     name = saw.Column(u'name',
    ...                      saw.VARCHAR,
    ...                      primary_key=True)
    ...
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    ...     def __repr__(self):
    ...         return u'Person("%s")' % self.name


Create defined tables
---------------------

All classes that inheret from db.Model will be created as tables

    >>> db.create()
    >>> 'Person' in db.tables
    True

Insert, query and delete registers
----------------------------------

Lets add some persons with:

    >>> new_person = Person(name='Foo')
    >>> db.insert(new_person)

We can query the database like:

    >>> with db.query as query:
    ...     person = query(
    ...         db.tables.Person
    ...     ).filter_by(name='Foo').one()

    >>> assert person.name == 'Foo'

To delete this person you can do like:

    >>> db.delete(person) 

Check thaat it doesnt exists anymore

    >>> with db.query as query:
    ...     try:
    ...         person = query(
    ...             db.tables.Person
    ...         ).filter_by(name='Foo').one()
    ...     except db.NoResultFound:
    ...         pass

Updating a Person
-----------------

    >>> db.insert(Person(name='Bar'))
    >>> with db.query as query:
    ...     person = query(
    ...         db.tables.Person
    ...     ).filter_by(name='Bar').one()
    
    >>> person.name = 'Baz'
    >>> db.update(person)

    >>> with db.query as query:
    ...     person = query(
    ...         db.tables.Person
    ...     ).filter_by(name='Baz').one()

    >>> assert person.name == 'Baz'


That's all! If you would like to know more about how to make more complex
queries, you can read:

http://docs.sqlalchemy.org/en/rel_0_8/orm/query.html#sqlalchemy.orm.query.Query

