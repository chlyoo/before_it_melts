from models.db_manager import DBManager

class SingletonType(object):
    def __call__(self, cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

class ServiceManager():
    __metaclass__ = SingletonType
    _service = {}
    _dbmanager = DBManager()
    
    @staticmethod
    def register_service(service_name:str, service_instance):
        ServiceManager._service[service_name] = service_instance

    @staticmethod
    def get_service_map():
        return ServiceManager._service

    @staticmethod
    def get_service(service_name):
        return ServiceManager._service[service_name]
