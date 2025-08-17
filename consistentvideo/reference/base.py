from abc import ABCMeta, abstractmethod


class SynopsisAnalyzerBase(metaclass=ABCMeta):
    def __init__(self, synopsis=None):
        self.__synopsis = None
        self.__entity_list = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def synopsis(self):
        return self.__synopsis

    @synopsis.setter
    def synopsis(self, value):
        self.__synopsis = value

    @property
    def entity_list(self):
        return self.__entity_list

    @entity_list.setter
    def entity_list(self, value):
        self.__entity_list = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value


class EntityCreatorBase(metaclass=ABCMeta):
    def __init__(self, entity=None):
        self.__entity_draft = None
        self.__entity = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def entity_draft(self):
        return self.__entity_draft

    @entity_draft.setter
    def entity_draft(self, value):
        self.__entity_draft = value

    @property
    def entity(self):
        return self.__entity

    @entity.setter
    def entity(self, value):
        self.__entity = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value
