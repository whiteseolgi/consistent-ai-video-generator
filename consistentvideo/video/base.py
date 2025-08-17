from abc import ABCMeta, abstractmethod


class CutImageGeneratorBase(metaclass=ABCMeta):
    def __init__(self, entity=None):
        self.__cut = None
        self.__cut_image = None
        self.__ai_model = None
        self.__entity = entity

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


class VideoGeneratorBase(metaclass=ABCMeta):
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


class VideoPostprocessorBase(metaclass=ABCMeta):
    def __init__(self, video=None):
        self.__video = None
        self.__processed_video = None
        self.__ai_model = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def video(self):
        return self.__video

    @video.setter
    def video(self, value):
        self.__video = value

    @property
    def processed_video(self):
        return self.__processed_video

    @processed_video.setter
    def processed_video(self, value):
        self.__processed_video = value

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value

class ImageGeneratorAIBase(metaclass=ABCMeta):
    def __init__(self):
        self.__ai_model = None
        self.__prompt_text = None
        self.__prompt_images = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value

    @property
    def prompt_text(self):
        return self.__prompt_text

    @prompt_text.setter
    def prompt_text(self, value):
        self.__prompt_text = value

    @property
    def prompt_images(self):
        return self.__prompt_images

    @prompt_images.setter
    def prompt_images(self, value):
        self.__prompt_images = value

class VideoGeneratorAIBase(metaclass=ABCMeta):
    def __init__(self):
        self.__ai_model = None
        self.__prompt_text = None
        self.__prompt_images = None

    @abstractmethod
    def execute(self):
        pass

    @property
    def ai_model(self):
        return self.__ai_model

    @ai_model.setter
    def ai_model(self, value):
        self.__ai_model = value

    @property
    def prompt_text(self):
        return self.__prompt_text

    @prompt_text.setter
    def prompt_text(self, value):
        self.__prompt_text = value

    @property
    def prompt_images(self):
        return self.__prompt_images

    @prompt_images.setter
    def prompt_images(self, value):
        self.__prompt_images = value
