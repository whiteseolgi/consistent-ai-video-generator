from abc import ABCMeta, abstractmethod


class SceneAnalyzerBase(metaclass=ABCMeta):
    def __init__(self, story=None):
        self.__story = None
        self.__scene_list = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def story(self):
        return self.__story

    @story.setter
    def story(self, value):
        self.__story = value

    @property
    def scene_list(self):
        return self.__scene_list

    @scene_list.setter
    def scene_list(self, value):
        self.__scene_list = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value


class CutGeneratorBase(metaclass=ABCMeta):
    def __init__(self, story=None):
        self.__scene = None
        self.__cut_list = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def scene(self):
        return self.__scene

    @scene.setter
    def scene(self, value):
        self.__scene = value

    @property
    def cut_list(self):
        return self.__cut_list

    @cut_list.setter
    def cut_list(self, value):
        self.__cut_list = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value
