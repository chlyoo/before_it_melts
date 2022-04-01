from models.db_manager import DBManager
from models.db_components import MongoDB
from melt_check import MeltCheck
from subscriptor import SubsCheck
import config
import schedule
import time

dbm = DBManager()

# AUTH
# subscript_redis = Redis(secrets.REDIS_URL, 6379)
meltcheck_mongo = MongoDB(config.MONGODB_URL,'meltcheck', 27017, config.MONGODB_ID, config.MONGODB_PW)
meltcheck_mongo.set_collection('menu')

# subscript mongo
subscript_mongo = MongoDB(config.MONGODB_URL,'subscriptor', 27017, config.MONGODB_ID, config.MONGODB_PW)
meltcheck_mongo.set_collection('subslist')

# REGISTER
# dbm.register_client('meltcheck_svc',subscript_redis)
dbm.register_client('subscript_db',meltcheck_mongo)
dbm.register_client('meltcheck_db',subscript_mongo)

# SVC
meltcheck_svc = MeltCheck(meltcheck_mongo, config.DEBUG)
subscription_svc = SubsCheck(subscript_mongo, config.DEBUG)

if __name__ == '__main__':
    schedule.every(10).minutes.do(meltcheck_svc._get_instance_menu)
    while True:
        schedule.run_pending()
        time.sleep(1)
