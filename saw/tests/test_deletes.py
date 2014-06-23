# -*- coding: utf-8 *-*

import saw
import unittest


class BaseTestDeletes(unittest.TestCase):
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
        self.Person = Person


class TestDeletes(BaseTestDeletes):

    def test_delete(self):

        db = self.db
        Person = self.Person

        db.insert(Person(name='Unit', lastname='Test'))

        with db.query as query:
            person = query(db.tables.Person).first()
            assert person is not None
            db.delete(person)
            assert query(db.tables.Person).first() is None
