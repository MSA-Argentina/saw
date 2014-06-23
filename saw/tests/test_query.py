import saw
import unittest


class BaseTestQuery(unittest.TestCase):
    """Base class for query tests classes."""

    def setUp(self):
        """Setup a test database."""
        self.db = saw.DB(name='unittests', engine='sqlite', in_memory=True)
        db = self.db

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

        self.Person = Person
        self.db.create()


class TestQuery(BaseTestQuery):
    """Test when we make queries."""

    def test_context_manager_query(self):
        """Lets query the db using db.autosession context manager."""

        db = self.db

        with db.query as query:
            persons = query(db.tables.Person).all()
        self.assertEquals(len(persons), 0)

        Person = self.Person
        db.insert(Person(name='Emiliano', lastname='Marcozzi'))

        with db.query as query:
            persons = query(db.tables.Person).all()
        self.assertEquals(len(persons), 1)


class TestQueryWithFilters(BaseTestQuery):
    """Test queries with filters."""

    def test_filter_by_name(self):
        """Add a person, then query for it."""

        db = self.db
        Person = self.Person

        with db.query as query:
            persons = query(db.tables.Person).filter_by(
                name='Foo').all()
        self.assertEquals(len(persons), 0)

        db.insert(Person(name='Foo', lastname='Bar'))

        with db.query as query:
            persons = query(db.tables.Person).filter_by(
                name='Foo').all()
        self.assertEquals(len(persons), 1)


if __name__ == '__main__':
    unittest.main()
