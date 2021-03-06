# -*- coding: utf-8 -*-
"""
    flask.ext.security.registerable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Flask-Security registerable module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""

from flask import current_app as app
from werkzeug.local import LocalProxy

from .confirmable import generate_confirmation_link
from .signals import user_registered
from .utils import do_flash, get_message, send_mail, encrypt_password

# Convenient references
_security = LocalProxy(lambda: app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def register_user(**kwargs):
    confirmation_link, token = None, None
    kwargs['password'] = encrypt_password(kwargs['password'])
    user = _datastore.create_user(**kwargs)
    _datastore.commit()

    if _security.confirmable:
        confirmation_link, token = generate_confirmation_link(user)
        do_flash(*get_message('CONFIRM_REGISTRATION', email=user.email))

        user_registered.send(dict(user=user, confirm_token=token),
                             app=app._get_current_object())

        send_mail('Welcome', user.email, 'welcome',
                  user=user, confirmation_link=confirmation_link)

    return user
