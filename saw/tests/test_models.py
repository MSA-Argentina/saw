# -*- coding: utf-8 *-*

import saw
import unittest


class BaseTestQuery(unittest.TestCase):
    """Base class for query tests classes."""

    def test_create_model(self):
        """Create a new model."""

        db = saw.DB(name='unittests', engine='sqlite', in_memory=True)
        assert 'Person' not in db.tables

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
        assert 'Person' in db.tables
