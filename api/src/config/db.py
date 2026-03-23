from dataclasses import dataclass
import os
from typing import Optional

@dataclass(frozen=True)
class DatabaseConfig:
    """
    A dataclass to hold database configuration parameters.
    """
    username: str
    password: str
    host: str
    database: str
    port: int
    type: str = 'postgresql'


def generate_connection_string(config):
    """
    Generate a database connection string based on the provided configuration.

    Args:
        config (DatabaseConfig): An instance of the DatabaseConfig dataclass containing database configuration parameters.

    Returns:
        str: A formatted database connection string.
    """
    db_type = config.type
    username = config.username
    password = config.password
    host = config.host
    port = config.port
    database = config.database

    if db_type == 'postgresql':
        return f"dbname={database} user={username} password={password} host={host} port={port}"
    elif db_type == 'mysql':
        return f"mysql://{username}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    

def get_database_connection(config):
    """
    Establish a connection to the database using the provided configuration.

    Args:
        config (DatabaseConfig): An instance of the DatabaseConfig dataclass containing database configuration parameters.

    Returns:
        connection: A database connection object.
    """
    connection_string = generate_connection_string(config)
    if config.type == 'postgresql':
        import psycopg2
        return psycopg2.connect(connection_string)
    elif config.type == 'mysql':
        import mysql
        return mysql.connector.connect(connection_string)
    else:
        raise ValueError(f"Unsupported database type: {config.type}")



BASE_CONFIG = DatabaseConfig(
    username=os.getenv("POSTGRES_USERNAME"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", 'localhost'),
    port=int(os.getenv("POSTGRES_PORT", 5432)),
    database="AcervoVivo"
)


class DatabaseContextManager:
    """
    A context manager for managing database connections.
    """
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config if config else BASE_CONFIG
        self.connection = None


    def __enter__(self):
        self.connection = get_database_connection(self.config)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
