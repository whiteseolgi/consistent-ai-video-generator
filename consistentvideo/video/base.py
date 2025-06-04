from abc import ABCMeta, abstractmethod


class CutImageGenerator(metaclass=ABCMeta):
    def __init__(self, entity=None):
        self.__cut = None
        self.__cut_image = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def entity(self):
        return self.__entity

    @entity.setter
    def entity(self, value):
        self.__entity = value

    @property
    def cut(self):
        return self.__cut

    @cut.setter
    def cut(self, value):
        self.__cut = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value


class VideoGenerator(metaclass=ABCMeta):
    def __init__(self, cut_image=None):
        self.__cut_image_list = None
        self.__video = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def cut_image_list(self):
        return self.__cut_image_list

    @cut_image_list.setter
    def cut_image_list(self, value):
        self.__cut_image_list = value

    @property
    def video(self):
        return self.__video

    @video.setter
    def video(self, value):
        self.__video = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value
