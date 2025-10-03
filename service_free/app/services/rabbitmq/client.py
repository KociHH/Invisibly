from shared.services.rebbitmq.client import PublicEmailRpcClient
from shared.services.rebbitmq.variables import NotificationsMQ
import logging
from config import RABBITMQ_URL
import asyncio
import json
import uuid
from aio_pika import connect_robust, Message, IncomingMessage, ExchangeType
import logging

logger = logging.getLogger(__name__)

class EmailRpcClient(PublicEmailRpcClient):
    def __init__(self, email: str, urlMQ: str = RABBITMQ_URL):
        super().__init__(urlMQ, email)
