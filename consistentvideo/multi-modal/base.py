from abc import ABCMeta, abstractmethod

class EntityReconstructorBase(metaclass=ABCMeta):
    def __init__(self, multi_modal_data : str = None, entity_image_directory_path : str = None):
        self.__multi_modal_data = multi_modal_data
        self.__entity_image_directory_path = entity_image_directory_path

    @abstractmethod
    def execute(self):
        pass

    @property
    def multi_modal_data(self):
        return self.__multi_modal_data

    @multi_modal_data.setter
    def multi_modal_data(self, value):
        self.__multi_modal_data = value

    @property
    def entity_image_directory_path(self):
        return self.__entity_image_directory_path

    @entity_image_directory_path.setter
    def entity_image_directory_path(self, value):
        self.__entity_image_directory_path = value


class MultiModalLoaderBase(metaclass=ABCMeta):
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

    @prompt_text.setter
    def prompt_images(self, value):
        self.__prompt_images = value