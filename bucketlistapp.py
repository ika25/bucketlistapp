from flask import Flask, request, session

from sqlalchemy import String
import re
import bcrypt
import os
from collections import namedtuple
from random import random
from sys import maxsize
from hashlib import sha1

from service.models import User, Todo, deleteTodoImage
from service.apimod import apierrorresponse, apiresponse, HttpInputError, HttpApiError, UnauthorizedAccessError, ApiContext
from config import DBCONFIG, SESSION_SECRET, VERBOSE, \
  STATIC_URL_PATH, STATIC_PATH, UPLOAD_PATH, UPLOAD_URL, \
  SUPPORTED_UPLOAD_IMAGES, PRODUCTION, API_PREFIX
# it will check for all config variables

from werkzeug.utils import secure_filename
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import sqlalchemy.sql.functions as sqlfunc

app = Flask(__name__, static_folder = STATIC_PATH, static_url_path = STATIC_URL_PATH)
app.config['SECRET_KEY'] = SESSION_SECRET
setattr(app, 'apictx', ApiContext(DBCONFIG, verbose=VERBOSE))

email_pttrn = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
def emailValidate(v):
  if email_pttrn.match(v) == None:
    raise HttpInputError("Invalid email has given")

def uploadImageValidate(f):
  f = request.files['image']
  if not f.content_type.startswith('image/'):
    raise HttpInputError("Uploaded image content type is not supported: %s" % f.content_type)
  (fbasename, fext) = os.path.splitext(secure_filename(f.filename))
  if fext.lower() not in SUPPORTED_UPLOAD_IMAGES:
    raise HttpInputError("Image extension is not supported: %s" % fext)

def orderByValidate(val, fn, allowed_cols=None, model=None):
  v = filter(lambda a: len(a) > 0, val.split(' '))
  if len(v) == 1: v.append(u'asc' if type(val) == unicode else 'asc')
  if len(v) != 2: 
    raise HttpInputError("Unexpected value for %s" % fn)
  v = map(unicode.strip if type(val) == unicode else str.strip, v)
  if allowed_cols != None and not v[0] in allowed_cols:
    raise HttpInputError("order_by should be one of (%s)" % ", ".join(allowed_cols))
  return (getattr(model, v[0]) if model != None else v[0],
          v[1].lower() == 'asc')

IntColumnDef = namedtuple("IntColumnDef", ('name', 'default', 'minval', 'maxval'))
def intsValidate(inp, colsdef):
  ret = {}
  for coldef in colsdef:
    val = inp.get(coldef.name, None)
    try:
      if val == None:
        val = coldef.default
        if val == None:
          raise HttpInputError("Input `%s' is required" % coldef.name)
      else:
        val = int(val)
        if coldef.minval != None:
          val = max(coldef.minval, val)
        if coldef.maxval != None:
          val = min(val, coldef.maxval)
      ret[coldef.name] = val
    except ValueError:
      raise HttpInputError("For input `%s', Integer expected" % coldef.name)
  return ret

def jsonFromRecord(item, columns):
  if item == None:
    return None
  record = {}
  for column in columns:
    if type(column) == dict:
      column_def = column
      column_name = column_def['name']
      column_type = column_def['type']
      if column_type == 'onerel':
        record[column_name] = jsonFromRecord(column_def['columns'], getattr(item, column_name))
    elif type(column) == tuple: # format
      if getattr(item, column[0]) != None:
        record[column[0]] = column[1] % str(getattr(item, column[0]))
      else:
        record[column[0]] = None;
    else:
      record[column] = getattr(item, column)
  return record
      

def simpleValidate(inp, model, fields, isRequired=True):
  udata = {}
  for cn in fields:
    val = inp.get(cn, '')
    if len(val) == 0:
      if isRequired:
        raise HttpInputError("Input `%s' is required" % cn)
      else:
        continue
    ftype = getattr(model, cn).type
    if isinstance(ftype, String) and ftype.length > 0 and \
       len(val) > ftype.length:
      raise HttpInputError("Input `%s' length limit exceeded, %d characters is allowed" % (cn, ftype.length))
    udata[cn] = val
  return udata


@app.errorhandler(HttpApiError)
def handle_api_error(error):
  return apierrorresponse(error)

# redirect 404 to static/index.html for development
if not PRODUCTION:
  @app.errorhandler(404)
  def handle_not_found_dev(error):
    return app.send_static_file('index.html')
# user methods

@app.route(API_PREFIX + '/register', methods=['POST'])
def register():
  udata = {}
  # required paramters
  # also check limit
  udata = simpleValidate(request.form, User, \
    ('username', 'password', 'first_name', 'last_name', 'email'))
  emailValidate(udata['email'])
  # check username availability
  with app.apictx.dbsession_scope() as dbs:
    if dbs.query(User).filter_by(username=udata['username']).count() > 0:
      raise HttpInputError("Username is not available!")
    salt = bcrypt.gensalt()
    udata['password'] = bcrypt.hashpw(udata['password'].encode('UTF-8'), salt).decode('UTF-8')
    user = User(**udata)
    dbs.add(user)
  return apiresponse({ }) # no need to send id

@app.route(API_PREFIX + '/login', methods=['POST'])
def login():
  for cn in ('username', 'password'):
    val = request.form.get(cn, '')
    if len(val) == 0:
      raise HttpInputError("`%s' is required" % cn)
  dbs = app.apictx.dbsession()
  try:
    user = dbs.query(User).filter_by(username=request.form['username']).one()
    try:
      if bcrypt.checkpw(request.form['password'].encode('UTF-8'), user.password.encode('UTF-8')):
        session['user_id'] = user.id
        return apiresponse({ })
    except ValueError:
      pass
  except MultipleResultsFound:
    raise Exception("Panic!, Multiple username is not allowed")
  except NoResultFound:
    pass
  finally:
    dbs.close()
  raise HttpApiError("Username or Password are not correct", 403)

@app.route(API_PREFIX + '/logout', methods=['GET'])
def logout():
  session.pop('user_id', None)
  return apiresponse({ })

@app.route(API_PREFIX + '/myInfo', methods=['GET'])
def myInfo():
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  minfo = {}
  for fn in ('username','email', 'first_name', 'last_name'):
    minfo[fn] = getattr(user, fn)
  return apiresponse({ 'record': minfo })

# Todo methods

def todoMkImageFN(todo, ext):
  maxattempt = 5
  name = sha1('%d-%d' % (todo.id, int(maxsize * random()))).hexdigest()+ext
  i = 0
  while os.path.exists(UPLOAD_PATH + name) and maxattempt > i:
    name = sha1('%d-%d' % (todo.id, int(maxsize * random()))).hexdigest()+ext
    i += 1
  if os.path.exists(UPLOAD_PATH + name):
    raise Exception("%d attempts to make a name for todo image failed" % maxattempt)
  return name
  

@app.route(API_PREFIX + '/todoCreate', methods=['POST'])
def todoCreate():
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  data = simpleValidate(request.form, Todo, ('title',))
  ints = intsValidate(request.form, [IntColumnDef('checked', 0, 0, 1)])
  data['checked'] = ints['checked']
  data['owner_id'] = user.id
  data['created_at'] = sqlfunc.current_timestamp()
  data['description'] = request.form.get('description', '')
  if 'image' in request.files:
    uploadImageValidate(request.files['image'])
  with app.apictx.dbsession_scope() as dbs:
    todo = Todo(**data)
    dbs.add(todo)
    dbs.commit()
    if 'image' in request.files:
      f = request.files['image']
      (fbasename, fext) = os.path.splitext(secure_filename(f.filename))
      ffn = todoMkImageFN(todo, fext)
      image_path = '%s/%s' % (UPLOAD_PATH, ffn)
      f.save(image_path)
      todo.image = ffn
    return apiresponse({ 'id': todo.id })

@app.route(API_PREFIX + '/todoUpdate/<todo_id>', methods=['POST'])
def todoUpdate(todo_id):
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  udata = simpleValidate(request.form, Todo, ('title',), False)
  ints = intsValidate(request.form, [IntColumnDef('checked', -1, 0, 1)])
  if ints['checked'] != -1:
    udata['checked'] = ints['checked']
  if 'description' in request.form:
    udata['description'] = request.form['description']
  if 'image' in request.files:
    uploadImageValidate(request.files['image'])
  with app.apictx.dbsession_scope() as dbs:
    td = dbs.query(Todo).filter_by(owner_id=user.id, id=todo_id).first()
    if td == None:
      raise HttpApiError("The todo item does not exists!", 404)
    if 'image' in request.files:
      deleteTodoImage(td)
      f = request.files['image']
      (fbasename, fext) = os.path.splitext(secure_filename(f.filename))
      ffn = todoMkImageFN(td, fext)
      image_path = '%s/%s' % (UPLOAD_PATH, ffn)
      f.save(image_path)
      udata['image'] = ffn
    elif 'image' in request.form:
      deleteTodoImage(td)
      udata['image'] = None
    for (fn, val) in udata.items():
      setattr(td, fn, val)
  return todo(todo_id)

def todoDelete(todo_id):
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  with app.apictx.dbsession_scope() as dbs:
    todo = dbs.query(Todo).filter_by(owner_id=user.id, id=todo_id).first()
    if todo == None:
      raise HttpApiError("The todo item does not exists!", 404)
    dbs.delete(todo)
  return apiresponse({ })

todo_columns = ('id', 'title', 'description',
                ('image', '%s/%%s' % UPLOAD_URL), 'checked')
@app.route(API_PREFIX + '/todos', methods=['GET'])
def todos():
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  (order_by, order_asc) = orderByValidate(request.args.get('order_by', 'id, asc'), 'order_by', ('title', 'id', 'created_at'), Todo)
  ints = intsValidate(request.args, (IntColumnDef('offset', 0, 0, None),
                                     IntColumnDef('limit', 10, 1, 1000),
                                     IntColumnDef('checked', -1, 0, 1)))
  filter_by_extra = {}
  if ints['checked'] != -1:
    filter_by_extra['checked'] = ints['checked']
  with app.apictx.dbsession_scope() as dbs:
    items = dbs.query(Todo) \
       .filter_by(owner_id=user.id, **filter_by_extra) \
       .order_by(order_by.asc() if order_asc else order_by.desc()) \
       .offset(ints['offset']).limit(ints['limit'])
    count = dbs.query(Todo) \
       .filter_by(owner_id=user.id, **filter_by_extra) \
       .count()
    return apiresponse({
      'records': [ jsonFromRecord(i, todo_columns) for i in items ],
      'count': count
    })
  

@app.route(API_PREFIX + '/todo/<todo_id>', methods=['GET','DELETE'])
def todo(todo_id):
  if request.method == 'DELETE':
    return todoDelete(todo_id)
  user = app.apictx.getUser()
  if user == None: raise UnauthorizedAccessError()
  dbs = app.apictx.dbsession()
  try:
    item = dbs.query(Todo).filter_by(owner_id=user.id,id=todo_id).one()
    return apiresponse({
      'record': jsonFromRecord(item, todo_columns)
    })
  except MultipleResultsFound:
    raise Exception("Panic!, Multiple value for filter pk is not allowed")
  except NoResultFound:
    raise HttpApiError("The todo item does not exists!", 404)
  finally:
    dbs.close()

  
