from abc import ABCMeta
import sys
from inspect import isclass, isabstract, getfile, getmro, getsource
from importlib import import_module
from typing import List, Callable, Dict
import logging
from functools import singledispatch
from re import sub

from pathlib import Path
from archtool.exceptions import (CheckFailedException,
                                 MultipleRealizationsException,
                                 RealizationNotFount)
from archtool.global_types import (
        Dependency,
        ContainerT,
        DependeciesT,
        AppModule,
        AppModules,
        DEPENDENCY_KEY,
        InterfaceT)


def string_to_snake_case(string: str):
    """
    Переводит любую строку в snake_case
    """
    string = sub('[<>]', '', string)
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        string.replace('-', ' '))).split()).lower()


@singledispatch
def resolve_import_path(obj: object) -> str:
    ...


@resolve_import_path.register
def _(obj: object) -> str:
    """
    """
    # TODO: docs
    base_dir = Path(sys.path[0]).parent
    file_path = getfile(obj)
    normailezed = file_path.replace(base_dir.absolute().as_posix(), "")
    normailezed = normailezed.replace("/", ".")[1:]
    normailezed = sub(r"\.py", "", normailezed)
    return normailezed


@resolve_import_path.register
def _(obj: str) -> str:
    # TODO: docs
    project_dir_name = Path(sys.path[0]).name
    if obj.startswith(project_dir_name):
        return obj
    absolute_path = f"{project_dir_name}.{obj}"
    return absolute_path


def inherits_from(child, parent_name):
    if isclass(child):
        if parent_name in [c.__name__ for c in getmro(child)[1:]]:
            return True
    return False


def get_subclasses_from_module(module_path: str,
                               superclass: type,
                               addiction_checks: List[Callable] = []
                               ) -> List[object]:
    """
    Достаёт классы-наследники из указанного модуля
    ARGS:
        module - модуль из которого тянем объекты
        superclass - класс-родитель, ищем его наследников
    """
    module_obj = import_module(module_path)
    app_module = AppModule(module_path)
    objects = []
    for key, obj in vars(module_obj).items():
        is_class = isclass(obj)
        # TODO: изменить механизм проверки
        buildin = key.startswith("__") and key.endswith("__")
        if any([buildin, not is_class]):
            continue

        # TODO:
        # из-за импорта id классов не совпадают, так что
        # inherits_from как временное решение.
        is_subclass = inherits_from(child=obj,
                                    parent_name=superclass.__name__)

        is_not_superclass = obj is not superclass
        module_absolute_path = resolve_import_path(app_module.import_path)
        try:
            imported_obj_absolute_path = resolve_import_path(obj)
        except TypeError:
            # обработка объектов у которых мы не можем получить getfile
            # пример: io.BytesIO
            continue
        is_imported = imported_obj_absolute_path != module_absolute_path
        logging.debug((f'\n{obj=}\n'
                       f'{is_not_superclass=}\n'
                       f'{module_absolute_path=}\n'
                       f'{imported_obj_absolute_path=}\n'
                       f'{is_imported=}'))
        try:
            if all([is_subclass, is_not_superclass, not is_imported]):
                for check in addiction_checks:
                    logging.debug('running_check:')
                    logging.debug((f'source: \n{getsource(check)}'))
                    check_result = check(obj)
                    logging.debug(f'{check_result=}')
                    if not check_result:
                        raise CheckFailedException(check)
                objects.append(obj)
        except CheckFailedException:
            continue
        finally:
            logging.debug('\n'*3)
    return objects


def get_class_instances_from_module(module_path: str,
                                    cls: type,
                                    addiction_checks: List[Callable] = []
                                    ) -> List[object]:
    """
    Достаёт инстансы класса из указанного модуля
    ARGS:
        module - модуль из которого тянем объекты
        cls - класc, ищем его инстансы
    """
    module_obj = import_module(module_path)
    objects = []
    for key, obj in vars(module_obj).items():
        is_instance = type(obj) is cls

        try:
            if is_instance:
                for check in addiction_checks:
                    check_result = check(obj)
                    if not check_result:
                        raise CheckFailedException(check)
                objects.append(obj)
        except CheckFailedException:
            continue
    return objects


def check_is_not_interface(obj):
    return not isabstract(obj)


def serialize_dep_key(key: DEPENDENCY_KEY) -> str:
    return f"{resolve_import_path(key.__module__)}.{key.__name__}"


def get_dependencies(container: ContainerT) -> DependeciesT:
    """
    Возвращает зависимости контейнера
    """
    dependencies: DependeciesT = []
    if not hasattr(container, "__annotations__"):
        return []

    for dependency_name, dependency in container.__annotations__.items():
        # вытащить аннотацию
        # TODO: ёбнуть проверку на является ли дочерним классом 
        # какого-либо слоя
        is_type_and_subclass = (type(dependency) in [type, ABCMeta])
        if all([is_type_and_subclass]):
            dep_key = serialize_dep_key(dependency)
            new_dep = Dependency(name=dependency_name, asked=dep_key)
            dependencies.append(new_dep)
    return dependencies


def get_module_interfaces(module: AppModule, superclass: object
                          ) -> List[InterfaceT]:
    """
    Возвращает
    """
    layer_module_path = f"{module.import_path}.interfaces"
    results = get_subclasses_from_module(module_path=layer_module_path,
                                         superclass=superclass,
                                         addiction_checks=[isabstract])
    return results


def get_interface_realization(module: AppModule,
                              name_pattern: str,
                              interface: InterfaceT) -> type:
    """
    Возвращает реализацию интерфейса в рамках модуля слоя

    ARGS:
     - module - модуль в котором ищеим реализации интерфейсов
     - name_pattern - паттерн имени файлов по которым ведётся поиск


    Возможные ошибки:
     - MultipleRealizationsException - нейдено больше одного класса,
                                       наследуемого от интерфейса

     - RealizationNotFount - реализация интерфейса не найдена
    """
    # TODO: сделать name pattern регулярным выражением
    # TODO: функция занимается поиском не только интерфейсов,
    #       если я не путаюсь. Если так, её аргументы и название
    #       надо переименовать
    module_path = f"{module.import_path}.{name_pattern}"
    module_layer_objects = get_subclasses_from_module(
        module_path=module_path,
        superclass=interface,
        addiction_checks=[check_is_not_interface])

    realizations_found = len(module_layer_objects)
    if realizations_found > 1:
        raise MultipleRealizationsException(str(f"{module=}\n\n",
                                                f"{interface=}\n\n",
                                                f"{module_layer_objects=}")
                                            )

    elif not realizations_found:
        raise RealizationNotFount((f"{module=}\n",
                                   f"{interface=}\n"))

    interface_realization = module_layer_objects[0]
    return interface_realization


def get_all_interfaces(app_modules: AppModules):
    """
    Достаёт все интерфейсы слоя из перечисленных модулей
    """
    interfaces = []
    for module in app_modules:
        module_interfaces = get_module_interfaces(module=module)
        interfaces.extend(module_interfaces)
    return interfaces


def get_all_interfaces_and_realizations(app_modules: AppModules,
                                        superclass,
                                        name_pattern: str
                                        ) -> Dict[InterfaceT, type]:
    """
    Достаёт все интерфейсы и классы их реализующие
    """
    interfaces_to_realizations = {}
    for module in app_modules:
        interfaces = get_module_interfaces(module=module,
                                           superclass=superclass)
        for interface in interfaces:
            realization = get_interface_realization(
                module=module,
                interface=interface,
                name_pattern=name_pattern)
            interfaces_to_realizations.update({interface: realization})

    return interfaces_to_realizations
