import asyncio
import json
import uuid
from aio_pika import connect_robust, Message, IncomingMessage, ExchangeType
import logging
from shared.services.rebbitmq.variables import NotificationsMQ

logger = logging.getLogger(__name__)

class PublicRpcClient:
    def __init__(self, urlMQ: str):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = asyncio.get_event_loop()
        self._connect_lock = asyncio.Lock()
        self.urlMQ = urlMQ

    async def connect(self):
        async with self._connect_lock:
            if self.connection and not self.connection.is_closed:
                return
            try:
                self.connection = await connect_robust(self.urlMQ)
                self.channel = await self.connection.channel()
                self.callback_queue = await self.channel.declare_queue(exclusive=True)

                await self.callback_queue.consume(self.on_response)
                logger.info("UserRpcClient connected to RabbitMQ.")
            except Exception as e:
                logger.error(f"UserRpcClient failed to connect to RabbitMQ: {e}")
                raise

    def on_response(self, message: IncomingMessage):
        if message.correlation_id in self.futures:
            future = self.futures.pop(message.correlation_id)
            future.set_result(json.loads(message.body.decode()))
        else:
            logger.warning(f"Received RPC response with unknown correlation_id: {message.correlation_id}")

    def clear_log_timeout(self, request_id: int, user_id: int | str):
        self.futures.pop(request_id)
        logger.error(f"RPC request to service_free for user {user_id} timed out.")
        return {"error": f"RCP request time out"}

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info(f"{__class__.__name__} connection closed.")


class PublicEmailRpcClient(PublicRpcClient):
    def __init__(self, email: str, urlMQ: str):
        super().__init__(urlMQ)
        self.email = email

    async def send_email_to_user(
        self,
        user_id: int | str,
        cause: str,
        size_code: int = 6
        ) -> dict:
        await self.connect() 

        correlation_id = str(uuid.uuid4())
        furure = self.loop.create_future()
        self.futures[correlation_id] = furure

        payload = {
            "user_id": user_id,
            "email": self.email,
            "cause": cause,
            "size_code": size_code
        }

        message = Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=NotificationsMQ.key
            )

        try:
            result = await asyncio.wait_for(furure, timeout=10)
            return result
        finally:
            self.futures.pop(correlation_id, None)
