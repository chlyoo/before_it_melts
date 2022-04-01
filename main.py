from models.db_manager import DBManager
from models.db_components import MongoDB
from melt_check import MeltCheck
from subscriptor import SubsCheck
import config
import schedule
import time

dbm = DBManager()

# AUTH
subscript_redis = Redis(secrets.REDIS_URL, config.redis_port)
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


if __name__ == '__main__':
    # Database Setup
    meltcheck_mongo = MongoDB(config.MONGODB_URL, 'meltcheck', 27017, config.MONGODB_ID, config.MONGODB_PW)
    meltcheck_mongo.set_collection('menu')
    ##### mongo subs collection
    # subscript_mongo = MongoDB(config.MONGODB_URL, 'subscriptor', 27017, config.MONGODB_ID, config.MONGODB_PW)
    # subscript_mongo.set_collection('subslist')
    subscript_redis = Redis(config.REDIS_URL, config.REDIS_PORT)

    # Service setup

    meltcheck_svc = MeltCheck(meltcheck_mongo, False)
    # meltcheck_svc = MeltCheck(meltcheck_mongo, config.DEBUG)
    # subsmongo_svc = SubsCheck(subscript_mongo, config.DEBUG)
    # subsredis_svc = SubsCheck(subscript_redis, config.DEBUG)

    bot = TelegramBot(subscript_redis, config.DEBUG)
    bot.register('meltcheck_mongo', meltcheck_svc)
    # bot.register('subs_mongo', subsmongo_svc)
    bot.register('subs_redis', subscript_redis)
    bot.run()
