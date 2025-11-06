from sqlalchemy.ext.asyncio.session import AsyncSession
from shared.services.websocket.manager import WSManager
from fastapi import HTTPException, WebSocket, status
from app.crud.user import ChatsProcess, RedisJsonsProcess
from app.db.redis.keys import __redis_chat_conns_ws__
import logging

logger = logging.getLogger(__name__)


class WSManagerChat(WSManager):
    def __init__(
        self, 
        user_id: str | int | None = None, 
        service: str = "chat"
        ):
        super().__init__(user_id, service)
        self._load_conns_from_redis()

    def _load_conns_from_redis(self):
        try:
            conns: list = __redis_chat_conns_ws__.get_cached() or []
            logger.debug(f"Загружено {len(conns)} пользователей из redis")
            return conns
        except Exception as e:
            logger.error(f"Ошибка при загрузке соединений из redis: {e}")
            return []

    def _save_conns_to_redis(self):
        try:
            active_user_ids = [str(uid) for uid in self.user_conns.keys() if self.user_conns[uid]]
            __redis_chat_conns_ws__.cached(active_user_ids)
            logger.debug(f"Сохранено {len(active_user_ids)} активных пользователей в Redis")
        except Exception as e:
            logger.error(f"Ошибка при сохранении соединений в redis: {e}")

    async def connect(self, user_id: str | int | None, ws: WebSocket):
        await super().connect(user_id, ws)
        self._save_conns_to_redis()

    async def disconnect(self, user_id: str | int | None, ws: WebSocket):
        await super().disconnect(user_id, ws)
        self._save_conns_to_redis()

    async def update_chats_for_users(
        self,
        participant_user_ids: list[str | int],
        db_session: AsyncSession, 
    ):
        """Обновляет кеш чатов для указанных пользователей"""
        for user_id in participant_user_ids:
            try:
                rjp = RedisJsonsProcess(user_id, None, db_session)
                payload = await rjp.get_or_cache_chats_user()
                
                await self.send_to_users([user_id], payload)
            except Exception as e:
                logger.error(f"Ошибка при обновлении чатов для пользователя {user_id}: {e}")
            
    async def update_history_chat_for_users(
        self,
        chat_id: str | int,
        calling_user_id: str | int,
        db_session: AsyncSession,
        ):
        """Обновляет кеш истории сообщений чата для всех пользователей"""
        try:
            rjp = RedisJsonsProcess(calling_user_id, chat_id, db_session)
            
            participant_ids = await rjp.get_or_cache_participans_chat()
            if not participant_ids:
                logger.error(f"Не найдены участники={participant_ids} чата: {chat_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participans not found in chat")    
            
            payload = await rjp.get_or_cache_message_history_private_chat()
            
            await self.send_to_users([participant_ids], payload)
        except Exception as e:
            logger.error(f"Ошибка при обновлении истории сообщений чата для пользователя {calling_user_id}: {e}")
          
        
wsc = WSManagerChat()