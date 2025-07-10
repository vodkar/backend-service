from dataclasses import dataclass


@dataclass
class Config:
    DEBUG: bool
    HOST: str
    PORT: int
    DATABASE_URI: str
