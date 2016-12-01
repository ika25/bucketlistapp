from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, ForeignKey, \
  DateTime, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.sql.functions as sqlfunc
import os
from config import UPLOAD_PATH

class Base(object):
  @declared_attr
  def __tablename__(cls):
    """ Name of table is derived from class name"""
    return cls.__name__.lower()
  """ all tables do have id primary_key """
  id = Column(Integer, primary_key=True)

metadata = MetaData()
Base = declarative_base(cls=Base, metadata=metadata)

class User(Base):
  username = Column(String(60), nullable=False, unique=True)
  password = Column(String(100), nullable=True)
  first_name = Column(String(100))
  last_name = Column(String(100))
  email = Column(String(100))
  todos = relationship("Todo", backref='user', single_parent=True,
                       cascade="all, delete, delete-orphan")
  def __repr__(self):
    return "<User username: %s (%s %s)>" % \
      (self.username, self.first_name, self.last_name)

class Todo(Base):
  owner_id = Column(Integer, ForeignKey('user.id'), index=True)
  title = Column(String(256), nullable=False)
  description = Column(Text) # can take care of big text
  image = Column(Text) # length does not matter
  checked = Column(Integer, nullable=False)
  created_at = Column(DateTime)
  def __repr__(self):
    return "<Todo %s \n%s\n%s  %s)>" % \
      (self.title, self.description, self.image, self.created_at)
  
def deleteTodoImage(target):
  try:
    os.remove('%s/%s' % (UPLOAD_PATH, target.image))
  except OSError as err:
    if err.errno != 2:
      raise err
  
def deleteTodoAssets(target):
  deleteTodoImage(target)
  
@event.listens_for(Todo, 'after_delete')
def todo_receive_after_delete(mapper, connection, target):
  deleteTodoAssets(target)

# standard decorator style
@event.listens_for(User, 'after_delete')
def user_receive_after_delete(mapper, connection, target):
  """listen for the 'after_delete' event"""
  for todo in target.todos:
    deleteTodoAssets(todo)
