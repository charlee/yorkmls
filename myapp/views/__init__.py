# -*- coding:utf8 -*-

from flask import render_template, session, request, redirect
from myapp import app
from myapp.core.user import current_user_id, j_require_login, require_login, url_for
from myapp.core.models import User, House
from myapp.core.house import run_import_houses_task
from .forms import MlsImportForm
from flask.ext.csrf import csrf_exempt

from myapp.utils.common import make_context

import users

@app.route('/')
@require_login()
def index():

  user = User.ref(current_user_id())

  house_ids = user.houses()
  houses = House.mget(house_ids)
  houses.sort(key=lambda x:x.add_date, reverse=True)

  context = make_context({ 'houses': houses })

  return render_template('index.html', **context)


@app.route('/rejected')
@require_login()
def rejected():

  user = User.ref(current_user_id())

  house_ids = user.rejected_houses()
  houses = House.mget(house_ids)
  houses.sort(key=lambda x:x.add_date, reverse=True)

  context = make_context({ 'houses': houses })

  return render_template('index.html', **context)
  

@app.route('/import/', methods=['GET', 'POST'])
@require_login()
def import_link():

  form = MlsImportForm(request.form)

  if request.method == 'POST' and form.validate():
    url = form.url.data
    run_import_houses_task(url)
    return redirect(url_for('index'))

  context = make_context({ 'form': form })
  return render_template('import.html', **context)



@app.route('/show/<house_id>')
@require_login()
def show(house_id):

  house = House.get(house_id)
  user = User.ref(current_user_id())

  if house:

    context = make_context({ 
      'house': house,
      'rejected': not user.has_house(house_id),
      'wantview': house.want_view == '1',
    })
    return render_template('show.html', **context)

  else:
    abort(404)


@app.route('/j/memo/<house_id>/', methods=['POST'])
@csrf_exempt
@j_require_login()
def update_memo(house_id):

  user_id = current_user_id()
  user = User.ref(user_id)

  if user.has_house(house_id):

    house = House.ref(house_id)
    memo = request.form['memo']

    house.update(memo=memo)

  return 'y'



@app.route('/j/reject/<house_id>/', methods=['POST'])
@csrf_exempt
@j_require_login()
def reject_house(house_id):

  user_id = current_user_id()
  user = User.ref(user_id)

  if user.has_house(house_id):

    user.reject_house(house_id)

  return 'y'

    

@app.route('/j/restore/<house_id>/', methods=['POST'])
@csrf_exempt
@j_require_login()
def restore_house(house_id):

  user_id = current_user_id()
  user = User.ref(user_id)

  if user.has_house_in_rejected(house_id):

    user.restore_house(house_id)

  return 'y'

    
@app.route('/j/wantview/<house_id>/', methods=['POST'])
@csrf_exempt
@j_require_login()
def wantview_house(house_id):

  user_id = current_user_id()
  user = User.ref(user_id)

  if user.has_house(house_id):

    house = House.ref(house_id)
    house.update(want_view='1')

  return 'y'

    
@app.route('/j/cancelview/<house_id>/', methods=['POST'])
@csrf_exempt
@j_require_login()
def cancelview_house(house_id):

  user_id = current_user_id()
  user = User.ref(user_id)

  if user.has_house(house_id):

    house = House.ref(house_id)
    house.update(want_view='0')

  return 'y'

