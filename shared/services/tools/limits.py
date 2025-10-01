import time
from slowapi import Limiter
from slowapi.util import get_remote_address
import requests

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
