import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def full_name_constructor(name: str | None, surname: str | None, if_isnone: str) -> str:
    full_name = ""
    if name:
        full_name += name
    if surname and name:
        full_name += f" {surname}"
    if surname and not name:
        full_name = surname if surname else if_isnone
    return full_name

def load_from_env(name: str, env_path: str = ".env") -> str | None:
    load_dotenv(env_path)
    exenv = os.getenv(name)
    if not exenv:
        logger.warning(f'Не найдено значение {name} в env файле [{env_path}]')
    return exenv