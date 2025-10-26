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

    async def send_change_email(
        self, 
        user_id_rjp: int | str,
        user_id: int | str,
        api_type: str,
        ):
        self.connect()

        correlation_id = uuid.uuid4()
        future = self.loop.create_future()
        self.futures[correlation_id] = future

        payload = {
            "user_id": user_id,
            "api_type": api_type,
            "rjp_data": {
                "user_id": user_id_rjp,
            }
        }

        message = Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=NotificationsMQ.key,
        )

        try:
            result = await asyncio.wait_for(future, timeout=10)
            return result
        finally:
            self.futures.pop(correlation_id)