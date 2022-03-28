class SingletonType(object):
    def __call__(self, cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

class DBManager():
    __metaclass__ = SingletonType
    _db = {}

    @staticmethod
    def register_client(u_service:str, db_utilizer):
        DBManager._db[u_service] = db_utilizer

    @staticmethod
    def get_db_map():
        return DBManager._db

    @staticmethod
    def get_db(u_service):
        return DBManager._db[u_service]
