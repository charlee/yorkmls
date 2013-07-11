# -*- coding:utf8 -*-

from flask import render_template, request, redirect, url_for
from myapp import app
from myapp.core.user import new_user, update_password, current_user_id, require_login, authenticate, login as user_login, logout as user_logout
from myapp.core.models import User
from myapp.utils.common import make_context

from forms import LoginForm, RegisterForm


@app.route('/login', methods=['POST', 'GET'])
def login():
  """
  User login
  """

  form = LoginForm(request.form)

  if request.method == 'POST' and form.validate():
    email = form.email.data
    password = form.password.data
    user_id = authenticate(email, password)
    if user_id:
      user_login(user_id)
      return redirect(url_for('index'))


  context = make_context({ 'form': form })
  return render_template('users/login.html', **context)
  


@app.route('/logout')
def logout():
  """
  User logout
  """
  user_logout()
  return redirect(url_for('index'))



@app.route('/register', methods=['POST', 'GET'])
def register():
  """
  User register
  """

  form = RegisterForm(request.form)

  if request.method == 'POST' and form.validate():
    email = form.email.data
    password = form.password.data

    user_id = new_user(email, password)

    user_id = authenticate(email, password)
    if user_id:
      user_login(user_id)
      return redirect(url_for('index'))

  context = make_context({ 'form': form })
  return render_template('users/register.html', **context)

