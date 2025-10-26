import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage, Message
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config import RABBITMQ_URL
from app.db.sql.settings import get_db_session
from app.crud.user import UserProcess
from shared.services.rebbitmq.variables import NotificationsMQ
from app.services.email import EmailProcess

logger = logging.getLogger(__name__)

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
                email = request_data.get("email", '')
                if email:
                    response_data = {"Not found key email in request_data"}

                    if action == NotificationsMQ.action_send_code_email_to_user:
                        cause = request_data.get("cause", '')
                        size_code = request_data.get("size_code", 6)

                        if cause:
                            response_data = self._send_code_email(email, cause, size_code)
                        else:
                            logger.error(f"Не найден ключ cause в request_data при получении данных ключа: {NotificationsMQ.action_send_code_email_to_user}")
                            response_data = {"error": "Not found key cause in request_data"}

                    if action == NotificationsMQ.action_send_change_email_user:
                        rjp_data = request_data.get("rjp_data", {})
                        if not rjp_data:
                            logger.error(f"Не найден ключ rjp_data в request_data при получении данных ключа: {NotificationsMQ.action_send_change_email_user}")
                            response_data = {"error": "Not found key rjp_data in request_data"}

                        api_type = request_data.get("api_type", '')
                        user_id_rjp = request_data.get("user_id")

                        if api_type and user_id_rjp:
                            response_data = self._send_change_email(email, self.user_id, api_type, user_id_rjp)
                        else:
                            keys_not_found = f"(api_type: {api_type}, user_id_rjp: {user_id_rjp})"
                            logger.error(f"Не найдены ключи {keys_not_found} в request_data при получении данных ключа: {NotificationsMQ.action_send_change_email_user}")
                            response_data = {"error": f"Not found keys {keys_not_found} in request_data"}

            response_message = Message(
                body=json.dumps(response_data).encode(),
                content_type="application/json",
                correlation_id=message.correlation_id,
            )

            await message.reply(response_message)

    def _send_code_email(
        self, 
        email: str,
        cause: str,
        size_code: int,
        ):
        ep = EmailProcess(email)

        sended = ep.send_code_email(cause, size_code)
        success = sended.get("success")

        if success:
            return {"code": sended.get("code"), "message": sended.get("message")}
        return {"error": sended.get("error")}

    def _send_change_email(
        self,
        email: str,
        user_id: int | str,
        api_type: str,
        user_id_rjp: int | str
        ):
        ep = EmailProcess(email)

        sended = ep.send_change_email(user_id, api_type, user_id_rjp)
        return sended


async def rabbit_init():
    connection = None
    try:
        mq = MQ()

        connection = await connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue(NotificationsMQ.key, durable=True)

        await queue.consume(mq.on_rpc_request)
        logger.info("Started User RPC Server in Service Notifications.")
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Failed to start User RPC Server: {e}")

    finally:
        if connection:
            await connection.close()
        else:
            logger.error(f"Значение connection не было задано: {connection}")
            return

