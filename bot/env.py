from environs import Env
from dataclasses import dataclass


@dataclass
class Config:
    TOKEN: str
    HOST_WAVELINK: str
    PORT_WAVELINK: int
    PASS_WAVELINK: str
    DATABASE: str


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        TOKEN=env.str("TOKEN_TEST"),
        HOST_WAVELINK=env.str("HOST_WAVELINK"),
        PORT_WAVELINK=env.str("PORT_WAVELINK"),
        PASS_WAVELINK=env.str("PASS_WAVELINK"),
        DATABASE=env.str("DATABASE"),
    )
