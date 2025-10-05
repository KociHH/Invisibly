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

l = load_from_env

class ConstructorUrl:
    def __init__(self) -> None:
        self._urls: dict[str, str] = {}
        self.build_urls()

    def build_urls(self):
        services = [
            'FREE', 'ADMIN', 'CHAT', 'FRIENDS', 
            'NOTIFICATIONS', 'PROFILE', 'SECURITY', 'SETTINGS'
        ]

        for service in services:
            host = l(f"SERVICE_{service}_HOST")
            port = l(f"SERVICE_{service}_PORT")

            if None in [host, port]:
                logger.error(f"Не найдены host: {host} или port: {port} сервиса {service}")
                return

            url = f"http://{host}:{port}"
            self._urls[service] = url
        return self._urls

constructor_url = ConstructorUrl()


def get_specific_url(service_name: str):
    url = constructor_url._urls.get(service_name)
    if not url:
        logger.warning(f"Юрл не найден для сервиса {service_name}: {url}")
    return url

def get_all_urls():
    return constructor_url._urls.copy()