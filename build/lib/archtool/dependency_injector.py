import typing as t
from typing import List, Dict
import logging

from .exceptions import (DependencyDuplicate,
                         DependencyDoesNotRegistred
                         )

from .interfaces import DependencyInjectorInterface

from archtool.layers.default_layers import default_layers
from archtool.layers.di_basic_layer import Layer
from archtool.components.default_component import ComponentPattern
from archtool.global_types import (AppModules,
                                   ContainerT,
                                   DEPENDENCY_KEY)

from archtool.utils import (get_dependencies,
                            serialize_dep_key,
                            get_all_interfaces_and_realizations)


# TODO: нахерачить документацию по тому как этим пользоваться
# TODO: валидации:
#       однонаправленность импортов

logging.basicConfig(
    format='[archtool.DependencyInjector]\t%(levelname)s:%(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)


T = t.TypeVar("T")


class DependencyInjector(DependencyInjectorInterface):
    def __init__(self,
                 modules_list: AppModules,
                 layers: List[Layer] = None):

        self.modules_list = modules_list
        # инициализируем классы слоёв
        # TODO: позже нужно вынести инициализацию.
        #       Это должен делать пользователь
        self._dependencies: Dict[DEPENDENCY_KEY, object] = {}

        self.layers = layers if layers else default_layers
        self._layers = []
        for layer in self.layers:
            initialized_layer = layer()
            self._layers.append(initialized_layer)
        self.layers = self._layers
        self._allowed_to_nested_injection: Dict[DEPENDENCY_KEY, bool] = {}

    def inject(self):
        logging.info('running injector...')
        logging.info(f'{self.modules_list=}')
        logging.info(f'{self.layers=}')

        for layer in self.layers:
            if issubclass(type(layer), Layer):
                for component_pattern in layer.component_groups:
                    # достаём модули, которые не игнорируют слой
                    modules_to_interact = self._exclude_ignored_modules(
                        component_pattern=component_pattern)

                    component_group_deps = get_all_interfaces_and_realizations(
                        app_modules=modules_to_interact,
                        name_pattern=component_pattern.module_name_regex,
                        superclass=component_pattern.superclass)

                    # добавляем зависимости слоя в глобальные зависимости
                    for dep_key, dep_class in component_group_deps.items():
                        # инициализируем классы, подставляем как зависимость
                        dep_instance = dep_class()
                        self._reg_dependency(key=dep_key,
                                            value=dep_instance)

        # инжектим
        line_sep = "\n\t"
        # logging.debug(f'dependencies:\n\t{line_sep.join(f"{key}: {val}" for key, val in self._dependencies.items() if str(key) and str(val))}')
        for dep_interface, dep_instance in self._dependencies.items():
            is_allowed_to_nested_injection = self._allowed_to_nested_injection[dep_interface]
            if not is_allowed_to_nested_injection:
                continue
            self._inject_dependencies(container=dep_instance)
        logging.info('injection ended')

    def _exclude_ignored_modules(self, component_pattern: ComponentPattern):
        filtered_modules = []
        for module in self.modules_list:
            if component_pattern not in module.ignore:
                filtered_modules.append(module)
        return filtered_modules

    def _inject_dependencies(self, container: ContainerT) -> None:
        """
        Внедряет зависимости

        ARGS:
        container - объект, в который встраиваем зависимости
        """
        deps = get_dependencies(container=container)
        for dep in deps:
            # пытаемся найти зависимость
            try:
                dependency_to_inject = self._get_dependency(key=dep.asked)
                setattr(container, dep.name, dependency_to_inject)
            except KeyError:
                raise DependencyDoesNotRegistred(("Данная зависимость не",
                                                 " зарегистрирована в",
                                                 " инжекторе"))

    def _reg_dependency(self,
                       key: DEPENDENCY_KEY,
                       value: object,
                       nested_injections_allowed: bool = True,
                       use_serialization_function: bool = True
                       ) -> None:
        """
        Проверяет существует ли зависимость.
        Если зависимости уже существует - возвращает ошибку DependencyDuplicate

        ARGS:
        key - ключ зависимости
        value - объект зависимости
        """
        if use_serialization_function:
            serialized_key = serialize_dep_key(key)
        else:
            serialized_key = key
        self._allowed_to_nested_injection.update({serialized_key: nested_injections_allowed})
        if serialized_key in self._dependencies:
            raise DependencyDuplicate(("Интерфейс зависимости должен быть",
                                      " уникальным.\n Зависимость с ключём",
                                      f" {key} уже зарегистрирована"))
        self._dependencies[serialized_key] = value

    def _get_dependency(self,
                        key: t.Union[str, T]) -> t.Union[object, T]:
        try:
            instance = self._dependencies[key]
            return instance
        except KeyError:
            serialized_deps =\
                  "\n\t".join(f"{key}: {item}"
                              for key, item in self._dependencies.items())
            raise DependencyDoesNotRegistred((
                f'Зависимость не найдена {key}\n'
                f'Dependencies:\n{serialized_deps}'))

    def get_dependency(self,
                       key: t.Union[str, T]) -> t.Union[object, T]:
        serialized_key = serialize_dep_key(key)
        return self._get_dependency(serialized_key)
