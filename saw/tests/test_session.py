# -*- coding: utf-8 *-*

import saw
import unittest


class BaseTestSession(unittest.TestCase):
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


class TestSession(BaseTestSession):
    """Test session."""

    def test_session_context_manager(self):

        db = self.db
        Person = self.Person

        with db.session as session:
            persons = session.query(db.tables.Person).all()
            assert len(persons) == 0

            session.add(Person(name='A', lastname='1'))
            session.commit()
            persons = session.query(db.tables.Person).all()
            assert len(persons) == 1

            session.add_all([
                Person(name='B', lastname='2'),
                Person(name='C', lastname='3'),
                Person(name='D', lastname='4'),
                Person(name='E', lastname='5'),
                Person(name='F', lastname='6'),
                Person(name='G', lastname='7'),
                ])
            session.commit()
            persons = session.query(db.tables.Person).all()
            assert len(persons) == 7

            session.query(db.tables.Person).delete()
            persons = session.query(db.tables.Person).all()
            assert len(persons) == 0


