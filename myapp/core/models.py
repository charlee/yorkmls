# -*- coding: utf8 -*-

"""
Define common ops for data models
"""


#######################################################################
# DESIGN PRINCIPLE
#
# 1. Class must deal with all keys related to itself
# 2. Don't touch objects from other classes (these should go to core.*, not models)
# 3. Instance methods should not rely on fields other than id;
#    so that a reference returned by Class.ref() can call all instance methods
#
#######################################################################

import re
from myapp import rds 
from pickle import loads
from datetime import datetime

# Link


class BaseModelMeta(type):

  def __init__(cls, name, bases, attrs):
    
    fields = {}

    # inherit fields from parent
    for base in bases:
      if hasattr(base, 'fields'):
        fields.update(base.fields)

    # overwrite base fields with own `fields`
    if attrs.has_key('fields'):
      fields = attrs['fields']

    # add extra fields if `extra_fields` defined
    if attrs.has_key('extra_fields'):
      fields.update(attrs['extra_fields'])

    cls.fields = fields

    # prepare for key name
    table_name = re.sub(r'([A-Z])', r'_\1', name)
    table_name = table_name[1:] if table_name[0] == '_' else table_name
    table_name = table_name.lower()

    # generate redis key name
    if not attrs.has_key('KEY'):
      cls.KEY = 'mls:' + table_name + ':%s'
      
    # generate auto_increment key name
    if not attrs.has_key('KEY_INCR'):
      cls.KEY_INCR = 'mls:' + table_name + ',incr'


class BaseHash:
  """Hash-type base model class"""

  __metaclass__ = BaseModelMeta

  def __init__(self, id, *args, **kwargs):

    # id is always str
    self.id = str(id)

    for field in self.fields.keys():

      default = self.fields[field]
      v = kwargs.get(field, str(default))

      # convert str to unicode
      if type(v) == str:
        v = v.decode('utf-8')

      setattr(self, field, v)

  def __repr__(self):
    keys = self.fields.keys()
    values = [getattr(self, key).encode('utf-8') for key in keys]
    attrs = ', '.join('%s=%s' % pair for pair in zip(keys, values))

    return "<%s: id=%s, %s>" % (self.__class__.__name__, self.id, attrs)

  def __unicode__(self):
    return self.__repr__()

  def as_hash(self):
    h = { 'id': self.id }
    for field in self.fields.keys():
      h[field] = getattr(self, field)
    return h
      
  @classmethod
  def get(cls, id, fields=None):
    """
    Get a single object
    """
    if not id:
      return

    if not fields:
      fields = cls.fields.keys()

    if not cls.exists(id):
      return None

    result = rds.hmget(cls.KEY % id, fields)

    return cls(id, **dict(zip(fields, result)))

  @classmethod
  def mget(cls, ids, fields=None):
    """
    Get multiple objects (with pipeline)
    """
    if not ids:
      return []

    if not fields:
      fields = cls.fields.keys()

    p = rds.pipeline()
    for id in ids:
      p.hmget(cls.KEY % id, fields)

    result = p.execute()

    return map(lambda pair: cls(pair[0], **dict(zip(fields, pair[1]))),
               zip(ids, result))

  @classmethod
  def exists(cls, id):
    """
    Check if an id exists in the database
    """
    return rds.exists(cls.KEY % id)

  @classmethod
  def _filter_params(cls, params):
    """
    Filter kwargs to pre-defined fields
    """
    return dict((k, v) for (k, v) in params.iteritems() if k in cls.fields)

  @classmethod
  def ref(cls, id):
    """
    Get the object reference by id.
    This method makes sure that the id exists, but will not fill any fields.
    """
    if cls.exists(id):
      return cls(id)
    else:
      return None


  @classmethod
  def new(cls, id=None, **kwargs):
    """
    Add a new object and return added id
    """
    
    if not id:
      # generate auto increment id
      id = rds.incr(cls.KEY_INCR)
      while cls.exists(id):
        id = rds.incr(cls.KEY_INCR)

    # add data to db
    params = cls._filter_params(kwargs)
    rds.hmset(cls.KEY % id, params)

    return id
    

  def update(self, **kwargs):
    """
    Update current object
    """
    
    # update data to db
    params = self._filter_params(kwargs)
    rds.hmset(self.KEY % self.id, params)

    # update object
    for k, v in kwargs.iteritems():
      setattr(self, k, v)

  @classmethod
  def remove(cls, id):
    """
    Delete specified object
    """
    rds.delete(cls.KEY % id)



class House(BaseHash):
  
  """
  Property model. use "House" as class name to avoid protential conflict with 'property'
  """


  KEY_REF_COUNT = 'mls:link:%s:ref_count'

  fields = {
    'address': '',
    'price': '',
    'pictures': '',
    'data': '',         # data table for this property
    'memo': '',
    'add_date': '',
  }

  def __init__(self, id, *args, **kwargs):
    super(House, self).__init__(id, *args, **kwargs)
    if self.pictures:
      self.pictures = loads(self.pictures)

    if self.add_date:
      self.add_date = datetime.fromtimestamp(int(self.add_date)).strftime('%Y/%m/%d')


  def ref_count(self):
    return rds.get(self.KEY_PIN_COUNT % self.id)


  def inc_ref_count(self):
    rds.incr(self.KEY_PIN_COUNT % self.id)


  def dec_ref_count(self):
    # TODO: make sure counter >= 0
    rds.decr(self.KEY_PIN_COUNT % self.id)
    

  @classmethod
  def remove(cls, id):
    """
    Delete a link
    """
    super(Link, cls).remove(id)

    # clear the counters
    p.delete(cls.KEY_REF_COUNT % id)
    


class User(BaseHash):

  # link references(SET)
  # used by core.pin.new_pin to check if user has already pinned a link
  KEY_HOUSES = 'mls:user:%s:houses'
  
  KEY_REJECTED_HOUSES = 'mls:user:%s:rejected-houses'

  # reverse ref (email -> user id) (HASH)
  # used by login and register check
  KEY_EMAIL_REF = 'fp:user:email:%s'

  fields = {
    'email': '',
    'password_digest': '',
  }

  @classmethod
  def new(cls, email, screen_name, password_digest):
    user_id = super(User, cls).new(email=email, screen_name=screen_name, password_digest=password_digest)
    rds.set(cls.KEY_EMAIL_REF % email, user_id)

    return user_id


  @classmethod
  def get_id_by_email(cls, email):
    """
    Get user id by Email
    """
    return rds.get(cls.KEY_EMAIL_REF % email)
    

  def add_house(self, house_id):
    """
    Add house to current user's house list
    """
    rds.sadd(self.KEY_HOUSES % self.id, house_id)


  def remove_house(self, house_id):
    """
    Remove house from current user's house list
    """
    rds.srem(self.KEY_HOUSES % self.id, 1, house_id)

  def reject_house(self, house_id):
    """
    Move house to rejected houses
    """
    rds.smove(self.KEY_HOUSES % self.id, self.KEY_REJECTED_HOUSES % self.id, house_id)

  def has_house(self, house_id):
    """
    Check if user has a house
    """
    return rds.sismember(self.KEY_HOUSES % self.id, house_id)

  def houses(self):
    """
    Get user's houses
    """
    return rds.smembers(self.KEY_HOUSES % self.id)

  def rejected_houses(self):
    return rds.smembers(self.KEY_REJECTED_HOUSES % self.id)


  def house_count(self):
    """
    Get house count
    """
    return rds.scard(self.KEY_HOUSES % self.id)


