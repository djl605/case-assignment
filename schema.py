from mongoengine import *
from os import environ

connect(host=environ['MONGO_DB'])

class UserShare(Document):
  ixPerson = IntField(required = True)
  shares = IntField(required = True)
  
  def serialize(self):
    return {'ixPerson': self.ixPerson, 'shares': self.shares}
  
class SiteData(Document):
  url = StringField(required = True, unique=True)
  is_https = BooleanField(required = True)
  token = StringField()
  shares = ListField(ReferenceField(UserShare))
  unique_id = StringField(required = True, unique = True)
  
  def serialize(self):
    return {'url': self.url, 'is_https': self.is_https, 'token': self.token, 'unique_id': self.unique_id, 'shares': [share.serialize() for share in self.shares]}