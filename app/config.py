from pydantic import BasicSettings
from typing import Optional
from functools import lru_cache


class BaseConfig(BasicSettings):
    ENV_STATE: Optional[str] = (
        None  # Variable To let our applicaiton know if it is on development, production or testing
    )

    class Config:
        # Class that tells pydantic to load a file to populate configuration variables via environment variables
        env_file: str = ".env"


class GlobalConfig(BaseConfig):
    # Class to tell pydantic which environment variables are gonna be read
    DATABASE_URL: Optional[str] = None  # Default value is none
    DB_FORCE_ROLL_BACK: bool = False  # Used to roll changes after every transaction so the database is not changed. Usefull when writting tests to rollback changes after finishing the test. This will be set to true in the tests


class DevConfig(GlobalConfig):
    class Config:
        env_prefix: str = (
            "DEV_"  # To prefix all env virables from the .env file with "DEV_"
        )


class TestConfig(GlobalConfig):
    # The environment variables harcoded here are the default the ones. These are overwritten with the ones in the .env file
    TEST_DATABASE_URL = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    class Config:
        env_prefix: str = (
            "PROD_"  # To prefix all env virables from the .env file with "DEV_"
        )


class ProdConfig(GlobalConfig):
    class Config:
        env_prefix: str = (
            "TEST_"  # To prefix all env virables from the .env file with "DEV_"
        )


@lru_cache()  # Environment variables are not supposed to change, so there is not need to completely load them every time the app refreshes, so caching increases performance.
def get_config(env_state: str):
    """Function to read and choose the environment variables based on the application mode defined in variable "ENV_STATE" """
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(
    BaseConfig().ENV_STATE  # Loads the env file
)  # Getting the value of the app mode out of the env variables
