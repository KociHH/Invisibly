import asyncio
import json
import uuid
from aio_pika import connect_robust, Message, IncomingMessage, ExchangeType
import logging
from shared.services.rebbitmq.variables import FreeMQ
from shared.services.rebbitmq.client import PublicUserRpcClient
from config.env import RABBITMQ_URL

logger = logging.getLogger(__name__)

class UserRpcClient(PublicUserRpcClient):
    def __init__(self, urlMQ: str = RABBITMQ_URL):
        super.__init__(urlMQ=urlMQ)

rpc_client = UserRpcClient()

