from abc import ABC, abstractmethod
from .layer import LayerInterface


class DILayerInterface(LayerInterface, ABC):
    # def __init__(self,
    #              superclass,
    #              module_name_pattern: str):

    #     self.superclass = superclass
    #     self.module_name_pattern = module_name_pattern

    @property
    @abstractmethod
    def Components(self):
        """
        Компоненты создаваемого слоя
        """
