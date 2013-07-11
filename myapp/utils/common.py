# -*- coding:utf8 -*-

from myapp.core.models import User
from myapp.core.user import current_user_id


def make_context(params):
    
  context = {}

  user_id = current_user_id()
  user = User.get(user_id)

  if user:
    context.update({ 'user': user })

  context.update(params)

  return context

