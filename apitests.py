import os
import unittest
import tempfile
import json
from random import random
from math import floor
from time import sleep
from io import BytesIO

from flask import Flask, url_for
from flask_testing import TestCase

from sqlalchemy import String

from service.apimod import ApiContext
from service.models import User, Todo

from bucketlistapp import app, SUPPORTED_UPLOAD_IMAGES, UPLOAD_PATH

def mulain(it, on):
  if not on:
    return False
  for i in it:
    if i not in on:
      return False
  return True

def mulin(it, on):
  if not on:
    return False
  for i in it:
    if i in on:
      return True
  return False

register_data = {
  'username': '_test',
  'password': '_test',
  'first_name': 'FNTest',
  'last_name': 'LNTest',
  'email': '_test@test.com'
}
def mk_todo_data(title='Todo Title', desc='Todo description'):
  return {
    'title': title,
    'description': desc,
    'image': (BytesIO(b'image data is here'), 'image.png'),
    'checked': 0
  }
def simpleValidateErrorCheck(client, fields, mkdata, model, rurl, isRequired, **argv):
  for cn in fields:
    # required test
    if isRequired:
      data = mkdata()
      data[cn] = ''
      rv = client.post(rurl, data=data, **argv)
      assert rv.status_code == 406 and \
        mulain((cn, 'required'), json.loads(rv.data).get('error_message')),\
        "%d: %s" % (rv.status_code, rv.data)
    ftype = getattr(model, cn).type
    if isinstance(ftype, String) and ftype.length > 0 :
      data = dict(register_data)
      data[cn] = ''.join(map(lambda a: 'a', xrange(ftype.length+1)))
      rv = client.post(rurl, data=data, **argv)
      assert rv.status_code == 406 and \
        mulain((cn, 'limit exceeded'), \
               json.loads(rv.data).get('error_message')),\
        "%d: %s" % (rv.status_code, rv.data)

def imageUploadValidateErrorCheck(client, fields, mkdata, model, rurl, pk, haspk):
  for cn in fields:
    for ext in SUPPORTED_UPLOAD_IMAGES:
      data = mkdata()
      idata = b'image data is here'
      data[cn] = (BytesIO(idata),
                  'image%s' % (ext if random() < 0.5 else ext.upper()))
      rv = client.post(rurl, data=data, content_type='multipart/form-data')
      assert rv.status_code == 200, "%d: %s" % (rv.status_code, rv.data)
      rdata = json.loads(rv.data)
      with app.apictx.dbsession_scope() as dbs:
        record = dbs.query(model).get(pk if haspk else rdata[pk])
        with open(UPLOAD_PATH + '/' + getattr(record, cn), 'rb') as f:
          assert f.read() == idata, "Data do not match!"
        if not haspk:
          dbs.delete(record)
          dbs.commit()
    data = mkdata()
    data[cn] = (BytesIO(b'image data is here'), 'doc.pdf')
    rv = client.post(rurl, data=data, content_type='multipart/form-data')
    rdata = json.loads(rv.data)
    assert rv.status_code != 200 and \
      ("content type is not supported" in rdata['error_message'] or \
       "Image extension is not supported" in rdata['error_message']), \
       "%d: %s" % (rv.status_code, rv.data)

class TestUserApi(TestCase):
  user_id=None
  @classmethod
  def setUpClass(cls):
    cls.delete_test_user()

  @classmethod
  def tearDownClass(cls):
    cls.delete_test_user()

  @classmethod
  def delete_test_user(cls):
    # get ready for test
    # delete _test user
    with app.apictx.dbsession_scope() as dbs:
      user = dbs.query(User).filter_by(username='_test').first()
      if user != None:
        dbs.delete(user)

  def initUserSession(self):
    assert self.__class__.user_id != None, "user_id has not saved!"
    with self.client.session_transaction() as sess:
      sess["user_id"] = self.__class__.user_id
  
  def create_app(self):
    global app
    app.config['TESTING'] = True
    return app

  def test_01_register(self):
    rurl = url_for('register')
    simpleValidateErrorCheck(self.client, ('username', 'password', 'first_name', 'last_name', 'email'), lambda: dict(register_data), User, rurl, True)
    # do register
    rv = self.client.post(rurl, data=register_data)
    assert rv.status_code == 200 and json.loads(rv.data).get('status') == 200,\
      "%d: %s" % (rv.status_code, rv.data)
  def test_02_login(self):
    rdata = register_data
    # login test start
    ldata = { 'username': rdata['username'], 'password': rdata['password'] }
    # wrong password test
    wrong_ldata = dict(ldata)
    wrong_ldata['password'] = 'wrong'
    rv = self.client.post(url_for('login'), data=wrong_ldata)
    assert rv.status_code == 403 and \
      json.loads(rv.data).get('status') == 403, \
      "%d: %s" % (rv.status_code, rv.data)
    # correct password
    rv = self.client.post(url_for('login'), data=ldata)
    assert rv.status_code == 200 and \
      json.loads(rv.data).get('status') == 200, \
      "%d: %s" % (rv.status_code, rv.data)
    with self.client.session_transaction() as sess:
      self.__class__.user_id = sess["user_id"]
  def test_03_myInfo(self):
    self.initUserSession()
    # myInfo
    rv = self.client.get(url_for('myInfo'))
    respdata = json.loads(rv.data)
    assert rv.status_code == 200 and \
      respdata.get('status') == 200 and \
      mulain(('username', 'first_name', 'last_name', 'email'), respdata.get('record', {})), \
      "%d: %s" % (rv.status_code, rv.data)
  def test_04_logout(self):
    self.initUserSession()
    # logout
    rv = self.client.get(url_for('logout'))
    respdata = json.loads(rv.data)
    assert rv.status_code == 200 and \
      respdata.get('status') == 200, \
      "%d: %s" % (rv.status_code, rv.data)
    # myInfo should return 403
    rv = self.client.get(url_for('myInfo'))
    respdata = json.loads(rv.data)
    assert rv.status_code == 403 and \
      respdata.get('status') == 403, \
      "%d: %s" % (rv.status_code, rv.data)
    
class TestTodoApi(TestCase):
  user_id=None
  todo_ids=[]
  todo_names=['T1', 't2', 'T3', 't4'] 
  @classmethod
  def setUpClass(cls):
    # create user and set user_id
    with app.apictx.dbsession_scope() as dbs:
      user = dbs.query(User).filter_by(username='_test').first()
      if user != None:
        dbs.delete(user)
        dbs.commit()
      rdata = { "username": "_test" }
      dbs = app.apictx.dbsession()
      user = User(**rdata)
      dbs.add(user)
      dbs.commit()
      cls.user_id = user.id

  @classmethod
  def tearDownClass(cls):
    with app.apictx.dbsession_scope() as dbs:
      user = dbs.query(User).filter_by(username='_test').first()
      if user != None:
        dbs.delete(user)
  
  def initUserSession(self):
    assert self.__class__.user_id != None, "user_id has not saved!"
    with self.client.session_transaction() as sess:
      sess["user_id"] = self.__class__.user_id


  def create_app(self):
    global app
    app.config['TESTING'] = True
    return app

  def test_01_todoCreate(self):
    self.initUserSession()
    rurl = url_for('todoCreate')
    simpleValidateErrorCheck(self.client, ('title',), mk_todo_data, Todo, rurl, True, content_type='multipart/form-data')
    imageUploadValidateErrorCheck(self.client, ('image',), mk_todo_data, Todo, rurl, 'id', False)
    create_todos = list(self.__class__.todo_names)
    while len(create_todos) > 0:
      idx = int(floor(random() * len(create_todos)))
      title = create_todos[idx]
      del create_todos[idx]
      data = mk_todo_data(title=title)
      rv = self.client.post(rurl, data=data, content_type='multipart/form-data')
      data = json.loads(rv.data)
      assert rv.status_code == 200 and \
        data['status'] == 200 and 'id' in data, \
        "%d: %s" % (rv.status_code, rv.data)
      self.__class__.todo_ids.append(data['id'])
      sleep(1)

  def test_02_updateTodo(self):
    self.initUserSession()
    todo_id = self.__class__.todo_ids[0]
    rurl = url_for('todoUpdate', todo_id=todo_id)
    simpleValidateErrorCheck(self.client, ('title',), lambda: dict(), Todo, rurl, False, content_type='multipart/form-data')
    imageUploadValidateErrorCheck(self.client, ('image',), lambda: dict(), Todo, rurl, todo_id, True)
    editval = 'editval'
    for cn in ('title','description'):
      with app.apictx.dbsession_scope() as dbs:
        record = dbs.query(Todo).get(todo_id)
        assert record != None
        origval = getattr(record, cn)
      with app.apictx.dbsession_scope() as dbs:
        data = { cn: editval }
        rv = self.client.post(rurl, data=data, content_type='multipart/form-data')
        record = dbs.query(Todo).get(todo_id)
        assert record != None and rv.status_code == 200 and \
          getattr(record, cn) == editval, \
          "%d: %s (if 200 change not matched)" % (rv.status_code, rv.data)
        setattr(record, cn, origval)

  def test_04_todo(self):
    self.initUserSession()
    todo_id = self.__class__.todo_ids[0]
    rurl = url_for('todo', todo_id=todo_id)
    rv = self.client.get(rurl)
    assert rv.status_code == 200 and \
      json.loads(rv.data)['record']['id'] == todo_id, \
          "%d: %s" % (rv.status_code, rv.data)
  
  def test_03_todos(self):
    self.initUserSession()
    # length match
    rurl = url_for('todos')
    rv = self.client.get(rurl)
    assert rv.status_code == 200 and \
      len(json.loads(rv.data)['records'])==len(self.__class__.todo_ids), \
      "%d: %s" % (rv.status_code, rv.data)
    # order test
    order_tests = (
      (tuple(self.__class__.todo_names), 'title', 'title'),
      (tuple(reversed(self.__class__.todo_names)),'title desc','title'),
      (tuple(self.__class__.todo_ids), 'id', 'id'),
      (tuple(self.__class__.todo_ids), 'created_at', 'id')
    );
    for (match, order_by, column) in order_tests:
      rurl = url_for('todos')
      rv = self.client.get(rurl, query_string=dict(order_by=order_by))
      assert rv.status_code == 200 and \
        tuple(map(lambda a:a[column],
                  json.loads(rv.data)['records'])) == match, \
        "%d: %s (order do not match)" % (rv.status_code, rv.data)

  def test_05_deleteTodo(self):
    self.initUserSession()
    todo_id = self.__class__.todo_ids[0]
    rurl = url_for('todo', todo_id=todo_id)
    rv = self.client.delete(rurl)
    with app.apictx.dbsession_scope() as dbs:
      record = dbs.query(Todo).get(todo_id)
      assert record == None and rv.status_code == 200, \
        "%d: %s (if 200 is not deleted)" % (rv.status_code, rv.data)
    

    

if __name__ == '__main__':
    unittest.main()
