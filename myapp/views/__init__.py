# -*- coding:utf8 -*-

from flask import render_template, session, request
from myapp import app
from core.user import current_user_id, require_login
from core.models import User
from forms import MlsImportForm

from utils.common import make_context

import houses
import users

@app.route('/')
@require_login()
def index():

  context = make_context({})

  return render_template('index.html', **context)



@app.route('/import/')
@require_login()
def import_link():

  form = MlsImportForm(request.form)

  if request.method == 'POST' and form.validate():
    url = form.url.data

  context = make_context({ 'form': form })
  return render_template('import.html', **context)
