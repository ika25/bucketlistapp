from flask import make_response, request, session
import json
from .models import User

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker # db Session

from contextlib import contextmanager

class HttpApiError(Exception):
  def __init__(self, message, status):
    self.status = status
    self.message = message

class HttpInputError(HttpApiError):
  def __init__(self, message, status=406):
    super(HttpInputError, self).__init__(message, status)

class UnauthorizedAccessError(HttpApiError):
  def __init__(self, message="Unauthorized access!", status=403):
    super(UnauthorizedAccessError, self).__init__(message, status)

def apierrorresponse(error):
  return make_response(json.dumps({ "status": error.status, "error_message": error.message }), error.status, {'Content-Type': 'application/json'})

def apiresponse(response):
  if 'status' not in response:
    response['status'] = 200
  return make_response(json.dumps(response), response['status'], {'Content-Type': 'application/json'})

class ApiContext(object):
  def __init__(self, DBCONFIG, verbose=False):
    self.dbe = create_engine(URL(DBCONFIG['DRIVER'], DBCONFIG['USER'], DBCONFIG['PASSWORD'], DBCONFIG['HOST'], DBCONFIG.get('PORT'), DBCONFIG['DBNAME']), echo=verbose)
    self.Session = sessionmaker(bind=self.dbe)
  def dbsession(self):
    if self.Session == None:
      raise Exception("dbsession called before initialization of dbengine")
    return self.Session()
  @contextmanager
  def dbsession_scope(self):
    """Provide a transactional scope around a series of operations."""
    session = self.Session()
    try:
      yield session
      session.commit()
    except:
      session.rollback()
      raise
    finally:
      session.close()
  def dispose(self):
    self.Session = None
    self.dbe = None
  def getUser(self):
    if 'user_id' in session:
      with self.dbsession_scope() as dbs:
        user = dbs.query(User).get(session['user_id'])
        if user != None:
          dbs.expunge(user)
        return user
    return None
