from dotenv import load_dotenv
import os
load_dotenv()

def load_from_env(name: str):
    return os.getenv(name)
l = load_from_env

NAME_PROJECT = l("NAME_PROJECT")
POSTGRES_URL = l("POSTGRES_URL")

UPORT = int(l("UPORT"))
UHOST = l("UHOST")