from enum import Enum


class DBType(Enum):
    MONGODB = 1
    REDIS = 2
    MYSQL = 3
    POSTGRESQL = 4
    UNKNOWN_TYPE = -1

    @staticmethod
    def resolve_type_from_str(name):
        if "MONGODB" == name.upper():
            return DBType.ASPECT
        elif "REDIS" == name.upper():
            return DBType.RUNTIME
        elif "MYSQL" == name.upper():
            return DBType.MYSQL
        elif "POSTGRESQL" == name.upper():
            return DBType.POSTGRESQL
        else:
            return DBType.UNKNOWN_TYPE

    @staticmethod
    def resolve_type_from_enum(enum):
        if enum == DBType.MONGODB:
            return "MONGODB"
        elif enum == DBType.REDIS:
            return "REDIS"
        elif enum == DBType.MYSQL:
            return "MYSQL"
        elif enum == DBType.POSTGRESQL:
            return "POSTGRESQL"
        else:
            return "UNKNOWN"


class CoreDBModel():
    def __init__(self, _client, _name, _type):
        # Model Type
        self._type = _type
        self._client = _client
        self._name = _name

    def set_type(self, _type):
        self._type = _type

    def set_name(self, _name):
        self._name = _name

    def get_name(self):
        return self._name

    def set_client(self, _client):
        self._name = _client

    def get_client(self):
        return self._client

    def get_type(self):
        return self._type
