import pymongo
import redis
from models.db_utilizer import DBUtilizer
from models.definition import DBType


class MongoDB(DBUtilizer):
    def __init__(self, URL, DB, PORT=27017, ID=None, PW=None):
        self._client = pymongo.MongoClient(f'mongodb://{ID}:{PW}@{URL}:{PORT}/{DB}')
        if (ID is None) and (PW is None):
            self._client = pymongo.MongoClient(f'mongodb://{URL}:{PORT}/{DB}')
        self._db = DB
        self._collection = None
        self.init_engine()

    def init_engine(self):
        # super().set_type(DBType.MONGODB)
        self._type = DBType.MONGODB
        self.set_db(self._db)

    def get_db(self):
        return self._db

    def get_collection(self):
        return self._collection

    def set_db(self, database: str):
        self._db = self._client[database]

    def set_collection(self, collection: str):
        self._collection = self._db[collection]


class Redis(DBUtilizer):
    def __init__(self, URL, PORT=6379, ID="Admin", PW=None, DB=0):
        self.client = redis.from_url(f'redis://{ID}:{PW}@{URL}:{PORT}/{DB}')
        if (ID is None) and (PW is None):
            self.client = redis.from_url(f'redis://{URL}:{PORT}')
        self.init_engine()

    def init_engine(self):
        # super().set_type(DBType.REDIS)
        self._type = DBType.REDIS

    def get_all_keys(self):
        return self.client.keys('*')

    def set_key(self,key, value):
        self.client.set(key, value)

    def get_key(self,key):
        return self.client.get(key)

    def delete_key(self, key):
        self.client.delete(key)