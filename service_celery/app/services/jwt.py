from dotenv import set_key, find_dotenv
import secrets
import logging
from config import SECRET_KEY, SECRET_KEY_SIZE
logger = logging.getLogger(__name__)

def generate_jwt_secretkey(recording_env: bool = False, env_path: str = ".env") -> None | str:
    dotenv_path = find_dotenv(env_path)
    new_secret_key = secrets.token_hex(SECRET_KEY_SIZE)
    
    if recording_env:
        if dotenv_path:
            set_key(dotenv_path, 'JWT_SECRET_KEY', new_secret_key)
            return new_secret_key
        else:
            logger.error(f"Не найден заданный путь к env: {env_path}")
            return
    else:
        return new_secret_key