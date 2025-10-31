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
        super().__init__(email, urlMQ)

    async def send_change_email(
        self, 
        user_id_rjp: int | str,
        user_id: int | str,
        api_type: str,
        ):
        await self.connect()

        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.futures[correlation_id] = future

        payload = {
            "user_id": user_id,
            "email": self.email,
            "action": NotificationsMQ.action_send_change_email_user,
            "api_type": api_type,
            "rjp_data": {
                "user_id": user_id_rjp,
            }
        }

        logger.info(f"Отправляем RabbitMQ запрос с correlation_id: {correlation_id}")
        logger.info(f"Payload: {payload}")

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
            logger.info(f"Получен результат для correlation_id {correlation_id}: {result}")
            self.cleanup_future(correlation_id)
            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for RabbitMQ response with correlation_id: {correlation_id}")
            self.cleanup_future(correlation_id)
            return {"success": False, "message": "Request timeout", "error": "Request timeout"}