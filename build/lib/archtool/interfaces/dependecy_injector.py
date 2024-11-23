from abc import ABC, abstractmethod
from archtool.global_types import AppModules, DEPENDENCY_KEY


class DependencyInjectorInterface(ABC):
    @abstractmethod
    def __init__(self,
                 modules_list: AppModules):
        """
        ARGS:
        - modules_list: список загружаемых модулей приложения
        """

    @abstractmethod
    def inject(self) -> None:
        """
        Внедряет зависимости во все репозитории и сервисы
        """

    @abstractmethod
    def get_dependency(self,
                       key: DEPENDENCY_KEY) -> object:
        """
        Ищет зависимость среди зарегистрированных

        ARGS:
        key - ключ зависимости (например интерфейс)
        """
