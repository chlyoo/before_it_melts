from models.definition import CoreDBModel


class DBUtilizer(CoreDBModel):
    def __init__(self):
        self._type = None
        pass

    def init_engine(self):
        pass

    def set_type(self, _type):
        self._type = _type

    def get_type(self):
        return self._type
