### Tutorial basic_example

Создадим структуру проекта

```
app
├── __init__.py
├── app.py
├── auth
|   ├── __init__.py
|   ├── interfaces.py
│   └── dtos.py
|
└── users
    ├── __init__.py
    ├── interfaces.py
    └── dtos.py

```


Файл app.py в корне проекта

```python
from archtool.dependency_injector import DependencyInjector
from archtool.layers.default_layers import DomainLayer
from archtool.global_types import AppModule

modules_list = [
    AppModule("users"),
    AppModule("auth")
]


injector = DependencyInjector(modules_list=modules_list)


if __name__ == "__main__":
    injector.inject()
    print("finish")
```


Напишем dto классы для интерфейсов сервисов, используем для этого pydantic в файле app/users/dtos.py


```python
import re
from pydantic import BaseModel, field_validator, ValidationError


class BaseUserProperties(BaseModel):
  first_name: str 
  lastname: str
  phone_number: str


class RetieveUserDTO(BaseUserProperties):
  id: int
  
  
class CreateUserDTO(BaseUserProperties):
  @field_validator('phone_number')
  def phone_number(cls, v):
    validate_phone_number_pattern = "^\+?7[0-9]{7,14}$"
    is_valid: bool = re.match(validate_phone_number_pattern, v)
    if is_valid:
      return v
    raise ValidationError("Value of field phone_number is incorrect.")

```


Напишем dto классы для модуля auth

```python
from pydantic import BaseModel

class TokenPair(BaseModel):
  access_token: str
  refresh_token: str
```


Теперь напишем интерфейсы наших сервисов


\
Файл interfaces.py в модуле users

```python
from abc import ABCMeta, abstractmethod
from archtool.layers.default_layer_interfaces import ABCService, ABCController, ABCRepo

from .dtos import CreateUserDTO, RetrieveUserDTO
from .datamappers import UserDM


class UserControllerInterface(ABCController, metaclass=ABCMeta):
  """
  Контроллер пользователя
  """
  @abstractmethod
  def get_or_create_user(self, user_data: CreateUserDTO) -> RetrieveUserDTO:
    """
    Создаёт либо возвращает пользователя
    """


class UserServiceInterface(ABCService, metaclass=ABCMeta):
  """
  Серавис пользователя
  """
  @abstractmethod
  def create_user(self, user: CreateUserDTO) -> RetrieveUserDTO:
    """
    Создаёт пользователя
    """
  
  def get_user_by_id(self) -> RetrieveUserDTO:
    """
    Позволяет получить пользователя по id
    """

  def delete_user(self, user_id: int) -> None:
    """
    Удаляет пользователя
    """


class UserRepoInterface(ABCRepo, metaclass=ABCMeta):
  """
  Репозиторий пользователя
  """  
  @abstractmethod
  def create_user(self, data: CreateUserData) -> RetrieveUserDTO:
    """
    Создаёт нового юзера
    """
```


Файл interfaces.py в модуле auth

```python
from abc import ABCMeta, abstractmethod
from archtool.layers.default_layer_interfaces import ABCService

from .dtos import TokenPair

class AuthServiceInterface(ABCService, metaclass=ABCMeta)
  
  def generate_tokens(self, user_id) -> TokenPair:
    """
    Создаёт токены сессии пользователя
    """

  def is_token_valid(self, token: str) -> bool:
    """
    Производит проверку токена. Возвращает True/False

    Args:
     - token: access либо refresh токен
    """
```


Теперь напишем реализации наших интерфейсов

создадим файл ./app/auth/services.py

```python
from app.users.interfaces import UserServiceInterface
from .interfaces import AuthServiceInterface


class AuthService(AuthServiceInterface):
  user_service: UserServiceInterface

  def generate_tokens(self, user_id) -> TokenPair:
    user = self.user_service.get_user(id=user_id)
    ... логика генерации jwt access и refresh токенов
    return TokenPair(access_token=access_token, refresh_token=refresh_token)

  def is_token_valid(self, token):
    ... логика проверки токена на валидность
    return is_token_valid
```

TODO: до писать
</br>
TODO: добавить проект в examples
</br></br>

создадим файл ./app/users/services.py

```python
from .interfaces import UserServiceInterface


class UserService(UserServiceInterface):
  user_repo: UserRepoInterface

  def generate_tokens(self, user_id) -> TokenPair:
    user = self.user_service.get_user(id=user_id)
    ... логика генерации jwt access и refresh токенов
    return TokenPair(access_token=access_token, refresh_token=refresh_token)

  def is_token_valid(self, token):
    ... логика проверки токена на валидность
    return is_token_valid
```
