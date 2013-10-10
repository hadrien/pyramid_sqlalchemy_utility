import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPCreated

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

log = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)


class UserGame(Base):

    __tablename__ = 'user_game'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    title = Column(String(100))
    score = Column(Integer)

    user = relationship("User", backref=backref('games', order_by=id))


def includeme(config):
    config.include('pyramid_sqlalchemy_utility')

    utility = config.get_sqlalchemy_utility()
    Base.metadata.create_all(utility.engine)

    config.add_route('users', pattern='/users')
    config.scan()


@view_config(route_name='users', request_method='POST')
def create_user(request):
    user = User()
    try:
        user.name = request.POST['name']
    except KeyError:
        raise HTTPBadRequest('no name parameter')

    request.sqla_session.add(user)

    return HTTPCreated()
