from abc import ABC


class ComponentPatternBase:
    ...


class ComponentPattern(ComponentPatternBase):
    def __init__(self,
                 module_name_regex: str,
                 superclass: ABC,
                 required: bool = True):
        """
        ARGS:
            module_name_regex - паттерн имени файла
            superclass - суперкласс наследники которого ищет injector
            required - обязателен ли модуль
        """
        self.superclass: ABC = superclass
        self.module_name_regex: str = module_name_regex
        self.required: bool = required
