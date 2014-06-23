# -*- coding: utf-8 *-*

import saw
import unittest


class BaseTestQuery(unittest.TestCase):
    """Base class for query tests classes."""

    def setUp(self):
        """Setup a test database."""

        db = saw.DB(name='unittests', engine='sqlite', in_memory=True)

        class Person(db.Model):

            __tablename__ = 'Person'

            name = saw.Column(u'name',
                        saw.VARCHAR,
                        primary_key=True)

            lastname = saw.Column(u'lastname',
                    saw.VARCHAR)

            def __init__(self, name, lastname):
                self.name = name
                self.lastname = lastname

            def __repr__(self):
                return "Person('%s' '%s')" % (self.name, self.lastname)

        db.create()
        self.db = db
        self.model = Person


class TestInserts(BaseTestQuery):

    def test_insert(self):

        db = self.db
        Person = self.model

        with db.query as query:
            assert query(db.tables.Person).filter(
                saw.and_(
                    Person.name == 'Unit',
                    Person.lastname == 'Test')).first() is None

        db.insert(Person(name='Unit', lastname='Test'))

        with db.query as query:
            assert query(db.tables.Person).filter(
            saw.and_(
                Person.name == 'Unit',
                Person.lastname == 'Test')).first() is not None

    def test_classic_insert(self):
        """Insert a registry opening a session, adding the new object to the
        session and closing the session."""

        db = self.db
        Person = self.model

        with db.query as query:
            assert query(db.tables.Person).filter(
                saw.and_(
                    Person.name == 'Unit',
                    Person.lastname == 'Test')).first() is None

        session = db.get_session()
        session.add(Person(name='Unit', lastname='Test'))
        session.commit()
        session.close()

        with db.query as query:
            assert query(db.tables.Person).filter(
            saw.and_(
                Person.name == 'Unit',
                Person.lastname == 'Test')).first() is not None


if __name__ == '__main__':
    unittest.main()
