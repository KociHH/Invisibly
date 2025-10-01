import asyncio
import json
import uuid
from aio_pika import connect_robust, Message, IncomingMessage, ExchangeType
import logging
from shared.services.rebbitmq.variables import FreeMQ
from config.env import RABBITMQ_URL

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


class PublicUserRpcClient(PublicRpcClient):
    def __init__(self, urlMQ: str):
        super().__init__(urlMQ)

    async def get_user_info(
        self, 
        user_id: int, 
        fields: list[str] | None = None,
        ) -> dict:
        await self.connect() 

        request_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.futures[request_id] = future

        request_body = {
            "user_id": user_id, 
            "action": FreeMQ.action_get_user_info
            }
        if fields:
            request_body["fields"] = fields

        message = Message(
            body=json.dumps(request_body).encode(),
            content_type="application/json",
            correlation_id=request_id,
            reply_to=self.callback_queue.name,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=FreeMQ.key,
        )

        try:
            response = await asyncio.wait_for(future, 10) 
            return response
        except asyncio.TimeoutError:
            return self.clear_log_timeout(request_id, user_id)
        except Exception as e:
            logger.error(f"Error call to service_free: {e}")
            return {"error": f"RPC call failed: {e}"}

    async def find_user_by_param(
        self,
        user_id: int | str, 
        param_name: str,
        param_value: str
        ):
        await self.connect()

        request_id = (uuid.uuid4())
        future = self.loop.create_future()
        self.futures[request_id] = future

        request_body = {
            "user_id": user_id,
            "action": FreeMQ.action_find_user_by_param,
            "param_name": param_name,
            "param_value": param_value,
        }

        message = Message(
            json.dumps(request_body).encode(),
            content_type="application/json",
            correlation_id=request_id,
            reply_to=self.callback_queue.name,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=FreeMQ.key
        )

        try:
            response = await asyncio.wait_for(future, 10)
            return response
        except asyncio.TimeoutError:
            self.clear_log_timeout(request_id, user_id)
        except Exception as e:
            logger.error(f"Error call to service_free: {user_id}")
            return {"error": f"RCP call failed {e}"}