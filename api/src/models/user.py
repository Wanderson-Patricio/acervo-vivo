from datetime import date, datetime

from ._base_class import BasePostgreSQLModel

class User(BasePostgreSQLModel):
    __tablename__ = '"Users"'

    name: str
    cpf: str
    birth_date: date
    address_id: int
    contact_id: int
    role_id: int
    registration_timestamp: datetime

    def name_validator(self, value: str):
        if (not value) or (not isinstance(value, str)):
            raise ValueError("User 'name' must be a non empty string.")
        
    def cpf_validator(self, value: str):
        def is_valid_cpf(cpf: str) -> bool:
            cpf = ''.join(filter(str.isdigit, cpf))
            if len(cpf) != 11 or cpf == cpf[0] * 11:
                return False

            for i in range(9, 11):
                sum = 0
                for j in range(0, i):
                    sum += int(cpf[j]) * ((i + 1) - j)
                digit = (sum * 10) % 11
                if digit == 10:
                    digit = 0
                if digit != int(cpf[i]):
                    return False
            return True
        
        if (not value) or (not isinstance(value, str)) or (not is_valid_cpf(value)):
            raise ValueError("User 'cpf' must be a valid CPF.")
        
    def birth_date_validator(self, value: date):
        if (not isinstance(value, date)) or (value >= date.today()):
            raise ValueError("User 'birth_date' must be a valid date in the past.")
        
    def address_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'address_id' must be a positive integer.")
        
    def contact_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'contact_id' must be a positive integer.")
        
    def role_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'role_id' must be a positive integer.")
        
    # def registration_timestamp_validator(self, value: datetime):
    #     if (not isinstance(value, datetime)) or (value > datetime.now()):
    #         raise ValueError("User 'registration_timestamp' must be a valid datetime in the past.")