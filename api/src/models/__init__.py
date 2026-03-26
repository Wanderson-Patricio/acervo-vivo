from ._base_class import BasePostgreSQLModel
from .role import Role, RoleCreate, RoleUpdate
from .address import Address, AddressRead, AddressCreate, AddressUpdate
from .contact import Contact, ContactRead, ContactCreate, ContactUpdate
from .authentication import Authentication, AuthenticationCreate, AuthenticationUpdate
from .user import User, UserRead, UserCreate, UserUpdate, UserRoleUpdate