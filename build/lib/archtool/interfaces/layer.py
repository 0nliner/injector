from abc import ABC, abstractmethod


class LayerInterface(ABC):
    @abstractmethod
    def __init__(self,
                 module_name_pattern: str,
                 depends_on: 'LayerInterface'):
        """
        ARGS:
        module_name_pattern - шаблон имени файла слоя (например ViewsLayer(module_name_pattern='views'))
        depends_on - слой, от которого зависит текущий слой
        """

    # @abstractmethod
    # def collect_items(self):
    #     """
    #     Собирает элементы слоя
    #     """

    # @abstractmethod
    # def _is_item(self, item: object):
    #     """
    #     Является ли элемент объектом слоя
    #     """
