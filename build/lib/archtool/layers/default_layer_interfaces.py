from abc import ABC


class ABCView(ABC):
    """
    Представление. Используйте для presentation layer
    """
    ...


class ABCController(ABC):
    ...


class ABCService(ABC):
    ...


class ABCRepo(ABC):
    ...


class ABCFacade(ABC):
    """
    Может быть использован для классов, реализующих паттерн фасад, например
    класс взаимодействующий со сторонним api
    """
    ...
