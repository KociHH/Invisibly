from typing import Any
from fastapi import Request
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql import UserRegistered
import uuid
import logging

logger = logging.getLogger(__name__)
PSWD_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
path_html = "app/frontend/src/html/"
# cd app/frontend

class GetUserInfo:
    def __init__(self, request: Request) -> None:
        self.request = request

    def get_ip_user(self) -> str | Any:
        client_ip = (
            self.request.headers.get("x-forwarded-for")
            or self.request.headers.get("x-real-ip")
            or self.request.headers.get("X-Envoy-External-Address")
            or self.request.client.host
        )

        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        return client_ip

    def get_device_type(self) -> dict[str, Any]:
        user_agent = self.request.headers.get("user-agent", "")
        devices = ["Mobi", "Android", "iPhone"]
        device_type = None

        for d in devices:
            if d in user_agent:
                device_type = "mobile"
                break

        if not device_type:
            device_type = "desktop"
        return {"device_type": device_type, "user_agent": user_agent}