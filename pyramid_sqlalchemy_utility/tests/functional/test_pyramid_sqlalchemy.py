import unittest

import webtest
from pyramid.config import Configurator

from ..import settings


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = cls.get_example_config()
        cls.sqla_utility = cls.config.get_sqlalchemy_utility()
        cls.app = webtest.TestApp(cls.config.make_wsgi_app())

    @classmethod
    def tearDownClass(cls):
        from example import Base
        utility = cls.config.get_sqlalchemy_utility()
        Base.metadata.drop_all(utility.engine)
        cls.sqla_utility.engine.pool.dispose()

    def tearDown(self):
        from example import User
        sqla_session = self.sqla_utility.session_cls()
        sqla_session.query(User).delete()
        sqla_session.commit()
        sqla_session.close()

    @classmethod
    def get_example_config(cls):
        from example import includeme
        config = Configurator(settings=settings)
        config.include(includeme)
        return config

    def test_row_creation(self):
        "row creation works"
        from example import User
        self.app.post('/users', params={'name': 'Bob Marley'})

        sqla_session = self.sqla_utility.session_cls()

        user = sqla_session.query(User).first()

        self.assertIsNotNone(user)

        sqla_session.close()
