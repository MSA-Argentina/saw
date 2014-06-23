# -*- coding: utf-8 *-*

import os
import threading

from contextlib import contextmanager
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc as sa_orm_exceptions
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base


class LocalTable(object):

    def __init__(self, db):
        self.db = db
        self.attrdict = db.mappedtables

    def __getattribute__(self, attr):
        adict = object.__getattribute__(self, 'attrdict')
        if attr in adict:
            return adict[attr]
        else:
            return object.__getattribute__(self, attr)

    def __setattribute__(self, name, value):
        adict = object.__getattribute__(self, 'attrdict')
        if name in adict:
            adict[name] = value
        else:
            object.__setattr__(self, name, value)

    def __iter__(self):
        return self.db.metadata.tables.iterkeys()

    def __len__(self):
        return len(self.db.metadata.tables.keys())

    def __contains__(self, attr):
        return attr in self.db.metadata.tables.keys()

    def keys(self):
        return self.db.metadata.tables.keys()


class SessionManager(object):
    """Handles the sessions in a multi-threaded environment.
    """

    def __init__(self, engine):
        self.engine = engine
        self._sessions = {}
        self.sessionmaker = sessionmaker(bind=self.engine)

    def get_session(self):
        """Return a session for this thread."""
        thread_id = threading.current_thread().ident
        try:
            return self._sessions[thread_id]
        except KeyError:
            pass

        session = self.sessionmaker()
        self._sessions[thread_id] = session
        return session

    def clean_session(self):
        """Remove, if found, session from self._sessions."""
        thread_id = threading.current_thread().ident
        try:
            return self._sessions[thread_id].pop()
        except KeyError:
            pass


class DB(object):

    # sqlalchemy orm exceptions
    NoResultFound = sa_orm_exceptions.NoResultFound
    MultipleResultsFound = sa_orm_exceptions.MultipleResultsFound
    ObjectDeletedError = sa_orm_exceptions.ObjectDeletedError
    exc = sa_orm_exceptions

    def __init__(self, name, engine, autoload=False, **kwargs):
        """A glorius Database.

        Arguments:
            name(str): name from the database.
            engine(str): name from the database engine, like:
                'sqlite', 'mysql', 'postgresql', 'oracle'
            autoload(bool): Reflect the database structure. It means that
                            automagically sqlalchemy guess all your tables
                            and coumns structures without the need of declaring
                            models.

        Optional arguments (depends on options given above):
            username='username'
            password='secret'
            host='127.0.0.1'

        If we use 'sqlite' as engine, we can give those extra cute options:
            in_memory(True)  If we want to create an in memory sqlite database,
                             really usefull for tests tasks..
            destdir = If its not in_memory, set this to the path where you want
                      the sqlite database file be created or the path to the
                      sqlite file that you want to open.

        Deep tweaks, optional engine parameters:
            pool_size=20  # how many connections to keep alive/established
            pool_recycle=3600  # time in seconds to recycle the connections
        """

        if not isinstance(engine, Engine):
            if engine == "sqlite":
                if kwargs.get('in_memory'):
                    engine = create_engine('sqlite:///:memory:')
                else:
                    if not os.path.isfile(name):
                        destdir = kwargs.get(
                            'destdir', os.path.abspath(os.path.curdir))
                        name = os.path.join(destdir, name)
                    engine = create_engine(
                        'sqlite:///{database}'.format(database=name)
                    )
            else:
                password = kwargs.get('password')
                if not password:
                    uri = '{engine}://{username}@{host}/{name}'.format(
                        engine=engine, username=kwargs['username'],
                        host=kwargs['host'], name=name)
                else:
                    uri = '{engine}://{username}:{password}@{host}/{name}'
                    uri = uri.format(
                        engine=engine, username=kwargs['username'],
                        password=password, host=kwargs['host'], name=name)

                engine = create_engine(
                    uri,
                    pool_size=kwargs.get("pool_size", 20),
                    pool_recycle=kwargs.get("pool_recycle", 3600))

        self._name = name
        self._engine = engine
        self._tables = dict()
        self._metadata = MetaData(bind=engine)
        self._session_manager = SessionManager(engine)

        if autoload:
            self._metadata.reflect(bind=engine)

        self.tables = LocalTable(self)
        self.create_mapped_tables()

    @property
    def Model(self):
        return declarative_base(metadata=self.metadata)

    @property
    def name(self):
        return self._name_

    @property
    def mappedtables(self):
        return self._tables

    @property
    def engine(self):
        return self._engine

    @property
    def metadata(self):
        return self._metadata

    @property
    def get_session(self):
        session_manager = self._session_manager
        return session_manager.get_session

    @property
    def clean_session(self):
        session_manager = self._session_manager
        return session_manager.clean_session

    @property
    @contextmanager
    def query(self):
        """session.query()"""
        session = self.get_session()
        yield session.query
        session.close()
        self.clean_session

    @property
    @contextmanager
    def session(self):
        """Autoclosing session"""
        session = self.get_session()
        yield session
        session.close()
        self.clean_session

    def create(self):
        """Create defined tables."""
        self.metadata.create_all(self.engine)
        self.create_mapped_tables()

    def insert(self, obj, returning_id=None):
        """Insert a new object."""
        session = self.get_session()
        try:
            session.add(obj)
            session.commit()
            if returning_id:
                returning_id = getattr(obj, returning_id)
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
            self.clean_session

        return returning_id

    def delete(self, obj):
        """Removes an object."""
        session = self.get_session()
        try:
            session.delete(obj)
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
            self.clean_session

    def update(self, obj):
        """Updates an object"""
        session = self.get_session()
        try:
            session.merge(obj)
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
            self.clean_session

    def create_mapped_tables(self):
        """Map on the fly created classes with metadata tables."""
        tablemapping = self._tables
        meta = self.metadata
        for tname in meta.tables:
            tname = str(tname)
            tablemapping[tname] = type(tname, (object,), dict())
            try:
                mapper(tablemapping[tname], meta.tables[tname])
            except Exception as exc:
                raise exc
