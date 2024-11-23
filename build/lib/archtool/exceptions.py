class CheckFailedException(Exception):
    ...


class UsedButIgnoredError(Exception):
    ...


class TopLevelLayerUsingException(Exception):
    ...


class DependencyDuplicate(Exception):
    ...


class DependencyDoesNotRegistred(Exception):
    ...


class MultipleRealizationsException(Exception):
    ...


class RealizationNotFount(Exception):
    ...
