import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage, Message
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.env import RABBITMQ_URL
from app.db.sql.settings import get_db_session
from app.crud.user import UserProcess
from shared.services.rebbitmq.variables import FreeMQ

logger = logging.getLogger(__name__)

# Пока не используется
class MQ:
    def __init__(self) -> None:
        self.user_id: int | str | None = None

    async def on_rpc_request(self, message: IncomingMessage):
        async with message.process():
            request_data = json.loads(message.body.decode())
            self.user_id = request_data.get("user_id")
            action = request_data.get("action")
            
            response_data = {"error": "Invalid action or user_id"}

            if self.user_id:
                if action == FreeMQ.action_get_user_info:
                    params_return: list = request_data.get("params", [])
                    response_data = await self.get_user_info_process(params_return)

                if action == FreeMQ.action_find_user_by_param:
                    param_name: str = request_data.get("param", "")
                    param_value: str = request_data.get("param_value", "")

                    if not param_name or not param_value:
                        logger.warning(f"Не был передан param_name или param_value в ключе {FreeMQ.key} action: {FreeMQ.action_find_user_by_param}")
                        response_data = {"error": "Not found param_name/param_value"}
                        yield

                    response_data = await self.find_user_by_param_process(param_name, param_value)

            response_message = Message(
                body=json.dumps(response_data).encode(),
                content_type="application/json",
                correlation_id=message.correlation_id,
            )

            await message.reply(response_message)

    async def get_user_info_process(self, params_return: list):
        async with get_db_session() as session:
            db_session: AsyncSession = session
                
            user_process = UserProcess(self.user_id, db_session)
            if db_session:
                full_user_data = await user_process.get_user_info(w_pswd=True, w_email_hash=True)
                
                if full_user_data:
                    if params_return:
                        filtered_data = {key: full_user_data.get(key) for key in params_return if key in full_user_data}
                        response_data = filtered_data
                    else:
                        response_data = {k: v for k, v in full_user_data.items() if k not in ['password', 'email_hash']}
                else:
                    response_data = {"error": "User not found", "user_id": self.user_id}
            else:
                response_data = {"error": "Database session could not be established"}

        return response_data

    async def find_user_by_param_process(self, param_name: str, param_value: str):
        async with get_db_session() as session:
            db_session: AsyncSession = session

        user_process = UserProcess(self.user_id, db_session)
        response_data = await user_process.find_user_by_param(param_name, param_value)

        return response_data


async def start_rpc_server():
    connection = None
    try:
        mq = MQ()

        connection = await connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue(FreeMQ.key, durable=True)

        await queue.consume(mq.on_rpc_request)
        logger.info("Started User RPC Server in Service Free.")
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Failed to start User RPC Server: {e}")

    finally:
        if connection:
            await connection.close()
        else:
            logger.error(f"Значение connection не было задано: {connection}")
            return

