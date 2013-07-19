pyramid_sqlalchemy_utility
==========================

A simple pyramid extension which register a sqlalchemy utility. It add a
`sqla_session` property to request object. Session is opened at first access
and automatically commited and closed on request's finished callback.

It tights sqlalchemy session to request lifecycle rather than relying on thread
local scoped sessions as recommended in sqlalchemy documentation:

    "The Session can be established as the request begins, or using a lazy
    initialization pattern which establishes one as soon as it is needed. The
    request then proceeds, with some system in place where application logic
    can access the current Session in a manner associated with how the actual
    request object is accessed. As the request ends, the Session is torn down
    as well, usually through the usage of event hooks provided by the web
    framework."

    -- http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html


Source code available on https://github.com/hadrien/pyramid_sqlalchemy_utility
