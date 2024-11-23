# TODO: расщепить типы

from abc import ABC
from dataclasses import dataclass, field
from typing import List, Any, Union
from re import Match
from pathlib import Path
import sys
from logging import getLogger

ContainerT = Any
InterfaceT = ABC



@dataclass
class Dependency:
    """
    ARGS:
    name - название зависимости
    asked - требуемая зависимость
    """
    name: str
    # что требуется заинжектить
    asked: Any


DependeciesT = List[Dependency]

DEPENDENCY_KEY = Union[InterfaceT, str, object]


@dataclass(repr=True)
class AppModule:
    """
    ARGS:
    - import_path: питонячий импорт модуля относительно BASE_DIR
    """
    import_path: str
    # TODO: перенести логику игнора слоёв
    ignore: List[Any] = field(default_factory=list)

    # TODO: написать отдельную функцию валидации модуля,
    # вынести её отдельно
    def _validate_module(self):
        """
        Производит проверки:
            - существует ли модуль
            - является ли он папкой
            - существуют ли интерфейсы в модуле
            - существуют ли репозитории в модуле
            - существуют ли сервисы в модуле
        """
        raise NotImplementedError()

    @property
    def absolute_import_path(self) -> str:
        """
        Возвращает полный путь до модуля
        """
        project_dir_name = Path(sys.path[0]).name
        absolute_path = f"{project_dir_name}.{self.import_path}"
        return absolute_path


AppModules = List[AppModule]


@dataclass
class ObjectMatch:
    module: AppModule
    obj: object


ObjectMatches = List[ObjectMatch]


@dataclass
class CodeMatch:
    module: AppModule
    match: Match


CodeMatches = List[CodeMatch]
