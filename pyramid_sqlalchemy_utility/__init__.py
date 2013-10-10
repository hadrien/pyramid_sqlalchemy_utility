import logging

from sqlalchemy.engine import engine_from_config
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import InvalidRequestError, DBAPIError

from zope.interface import Interface, implementer

log = logging.getLogger(__name__)


def includeme(config):
    engine = engine_from_config(config.registry.settings)

    utility = Utility(engine, sessionmaker(bind=engine))

    config.registry.registerUtility(utility)
    config.add_request_method(utility.open_session, 'sqla_session',
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
class Utility(object):

    def __init__(self, engine, session_cls):
        self.engine = engine
        self.session_cls = session_cls

    def new_session(self):
        return self.session_cls()

    def open_session(self, request):
        request.add_finished_callback(self._close_session)
        session = self.new_session()
        log.debug('Openning session %s', session)
        return session

    def _close_session(self, request):
        try:
            sqla_session = request.sqla_session
        except AttributeError:  # pragma: no cover
            log.exception('request.sqla_session does not exist')
            return

        log.debug('Commiting & closing session %s', sqla_session)

        try:
            sqla_session.commit()

        except InvalidRequestError:
            log.debug('Nothing to commit for session %s', sqla_session,
                      exc_info=True)

        except DBAPIError:
            log.exception('sqla_session.commit failed on %s', sqla_session)
            sqla_session.rollback()
            raise

        finally:
            sqla_session.close()
            delattr(request, 'sqla_session')
