import logging

from sqlalchemy.engine import engine_from_config
from sqlalchemy.orm.session import sessionmaker
from zope.interface import Interface, implementer

log = logging.getLogger(__name__)


def includeme(config):
    engine = engine_from_config(config.registry.settings)

    sql_alchemy_utility = SqlAlchemyUtility(engine, sessionmaker(bind=engine))

    config.registry.registerUtility(sql_alchemy_utility)
    config.add_request_method(sql_alchemy_utility.open_session, 'sqla_session',
                              reify=True)
    config.add_directive('get_sqlalchemy_utility',
                         directive_get_sqlalchemy_utility, action_wrap=False)


def directive_get_sqlalchemy_utility(config):
    return config.registry.getUtility(ISessionUtility)


def get_sqlalchemy_utility(registry):
    return registry.getUtility(ISessionUtility)  # pragma: no cover


class ISessionUtility(Interface):
    def __call__(self):
        "To create a sqlalchemy session"


@implementer(ISessionUtility)
class SqlAlchemyUtility(object):

    def __init__(self, engine, session_cls):
        self.engine = engine
        self.session_cls = session_cls

    def open_session(self, request):
        request.add_finished_callback(self.close_session)
        session = self.session_cls()
        log.debug('Openning sqlAlchemy session %s', session)
        return session

    def close_session(self, request):
        try:
            log.debug('Closing sqlAlchemy session %s', request.sqla_session)
            request.sqla_session.commit()
            request.sqla_session.close()
        except AttributeError:  # pragma: no cover
            log.exception('request.sqla_session does not exist')
