from typing import Optional
from pydantic import Field, BaseModel, root_validator
from pathlib import Path

class AiiDAProcessControlConfig(BaseModel):
    """Configuration of the AiiDA process control backend
    """
    broker_protocol: str = Field(
        "amqp",
        description=("Protocol to use for the message broker.")
    )
    broker_username: str = Field(
        "guest",
        description = ("Username to use for authentication with the message broker.")
    )

    broker_password: str = Field(
        "guest",
        description=("Password to use for authentication with the message broker.")
    )

    broker_host: str = Field(
        "127.0.0.1",
        description = ("Hostname for the message broker.")
    )

    database_port: int = Field(
        5672,
        description = ("Port for the message broker.")
    )

    broker_virtual_host: str = Field(
        "",
        description= ("Name of the virtual host for the message broker without leading forward slash.")
    )


class AiiDAStorageConfig(BaseModel):
    """Configuration of the AiiDA storage backend
    """
    database_engine: str = Field(
        'postgresql_psycopg2',
        description=('Database engine')
    )

    database_hostname:str = Field(
        'localhost',
        description=('Hostname for the database')
    )

    database_port:int = Field(
        5432,
        description=('Port number for the database.')
    )

    database_name : str = Field(
        ...,
        description=('Database name')
    )

    database_username : str = Field(
        ...,
        description = ('Database user name')
    )

    database_password : str = Field(
        ...,
        description = ('Secret database password')
    )

    repository_uri : Optional[str] = Field(
        None,
        description = ('URI of the AiiDA repository')
    )

class AiiDAStorage(BaseModel):
    """AiiDA Storage configuration
    """
    backend: str = Field(
        "psql_dos",
        description=("backend")
    )

    config: AiiDAStorageConfig = Field(
        ...,
        description=("Storage")
    )


class AiiDAProcessControl(BaseModel):
    """ Simplified AiiDA Process control datamodel.
    """
    backend: str = Field(
        "rabbitmq",
        description=("backend")
    )

    config: AiiDAProcessControlConfig = Field(
        AiiDAProcessControlConfig(),
        description=("Process Controll Configuration")
    )

class AiiDAProfileConfig(BaseModel):
    """Simplified AiiDA Profile Configuration

    """
    profile_name: str = Field(
        ...,
        description=("Profile name")
    )

    storage: AiiDAStorage = Field(
        ...,
        description=("Storage backend config")
    )

    process_control: AiiDAProcessControl = Field(
        AiiDAProcessControl(),
        description=("Message Queue")
    )

    @root_validator(pre=True)
    def storage_repository_url(cls, values):
        """Validator for custom initialization of the repository_uri property.
        As the profile_name is given as a property upon initialization, this
        validator will use this value to construct the storage.config.repository_uri
        """
        home = str(Path.home())
        rep_url = f'file://{home}/.aiida/repository/{values["profile_name"]}'
        values["storage"]["config"]["repository_uri"] = rep_url
        return values