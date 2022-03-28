from models.definition import DBType
from datetime import datetime
import json


class SubsCheck():
    def __init__(self, dbu, debug):
        self.dbu = dbu
        self.db = self.dbu.get_db()
        self.collection = None
        if self.dbu.get_type() == DBType.MONGODB:
            self.collection = self.dbu.get_collection()

    def init_mongo_db(self):
        print("initialize mongo db for first install")
        self.collection.insert_one({"menu": self.menu_data, "date": datetime.now().strftime('%y%m%d %HH')})

    def get_subscriptors(self):
        cursor = self.collection.find()
        for record in cursor:
            print(record)
        return self.subscriptors

    def append_subscription(self, target):
        self.subscriptors.append(target)

    def subscribe(self, chat_id):
        self.collection.update_one(
            {"id": chat_id}, {"$set": {"state": "active", "date": datetime.now().strftime('%y%m%d %h:%m:%s')}},
            upsert=True)

    def unsubscribe(self, chat_id):
        query_filter = {"id": chat_id}
        new_value = {"state": "inactive", "date": datetime.now().strftime('%y%m%d %h:%m:%s')}
        self.collection.update_one(query_filter, new_value)

    def get_db_subscription(self):
        results = self.collection.find({"state": "active"})
        return [value['id'] for value in results]
