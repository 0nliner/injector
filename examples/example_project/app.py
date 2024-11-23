import sys
import pathlib

sys.path.append(pathlib.Path.cwd().as_posix())

from archtool.dependency_injector import DependencyInjector
from archtool.layers.default_layers import DomainLayer
from archtool.global_types import AppModule
from test_module_1.interfaces import TestRepo1Interface


#   ignore=[DomainLayer.Components.services]),
modules_list = [
    AppModule("test_module_1"),
    AppModule("test_module_2")
]

injector = DependencyInjector(modules_list=modules_list)

if __name__ == "__main__":
    injector.inject()
    injector.get_dependency(TestRepo1Interface)
    print("finish")
