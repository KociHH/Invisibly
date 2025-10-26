from fastapi import HTTPException
from kos_Htools.redis_core import RedisBase
from kos_Htools.sql.sql_alchemy import BaseDAO
from sqlalchemy import and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from service_chat.app.db.redis.keys import RedisUserKeys
from app.db.sql.models.personal_user import UserChat, Message, ChatParticipant
from shared.services.tools.other import full_name_constructor
import logging
from shared.crud.sql.user import UserCRUD
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class ChatsProcess(RedisUserKeys):
    def __init__(
        self, 
        user_id: int | str, 
        db_session: AsyncSession
        ) -> None:
        super().__init__(user_id)
        self.db_session = db_session
        
        self.chat_parti_dao = BaseDAO(ChatParticipant, self.db_session)
        self.user_chat_dao = BaseDAO(UserChat, self.db_session)
        self.message_dao = BaseDAO(Message, self.db_session)

    async def get_chats_participants_user(self) -> dict:
        """
        return *example: `{chat_id: [uid1, uid2], ...} or {}`
        """
        try:
            user_chats = await self.chat_parti_dao.get_all_column_values(
                ChatParticipant.chat_id,
                ChatParticipant.user_id == self.user_id
            )
        
            result_chat_info = {}
            if user_chats:
                for chat_id in user_chats:
                    user_in_chat: list = await self.chat_parti_dao.get_one_ordered_or_none(
                        ChatParticipant.user_id,
                        ChatParticipant.chat_id == chat_id
                    )
                
                    user_in_chat_clear = [uid for uid in user_in_chat if uid != self.user_id]
                    if user_in_chat_clear:
                        for uid in user_in_chat_clear:
                            result_chat_info[chat_id] = [self.user_id, uid]

            return result_chat_info
        except Exception as e:
            logger.error(f"Ошибка в функции get_chats_participants_user: {e}")
            raise HTTPException(status_code=500, detail="Server error")

    async def get_or_cache_chats(self) -> dict:
        chat_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}

        if not chat_data:
            chats = await self.chat_parti_dao.get_all_column_values(
                (UserChat.user1_id, UserChat.user2_id, UserChat.id, UserChat.created_at),
                and_(UserChat.user1_id == self.user_id, UserChat.user2_id == self.user_id)
            )

            if chats:
                chats.sort(lambda f: f[2])
                
                for chat_pack in chats:
                    user1_id = chat_pack[0]
                    user2_id = chat_pack[1]
                    chat_id = chat_pack[2]

                    messages = await self.message_dao.get_all_column_values(
                        Message.content,
                        and_(Message.chat_id == chat_id, Message.id),
                        order_by=(desc(Message.id),),
                        limit=1
                    )

                    last_message = messages[0][0]

                    user_content = user1_id
                    if user_content == self.user_id:
                        user_content = user2_id
                    
                    id_chat = chat_pack[2]
                    
                    chat_user_info = await _http_client.find_user_by_param("user_id", user_content)

                    full_name = full_name_constructor(chat_user_info.get("name"), chat_user_info.get("surname"))
                        
                    chat_data[id_chat] = {
                        "full_name": full_name,
                        "last_message": last_message,
                        "id_chat": id_chat
                    }

                self.chat_obj.checkpoint_key.cached(chat_data)
            return chat_data
        else:
            return chat_data


class MessageProcess:
    def __init__(
        self,
        chat_id: int | str,
        user_id: int | str,
        ):
        self.chat_id = chat_id
        self.user_id = user_id
        
    async def message_history_chat_user(self, db_session: AsyncSession) -> dict:
        """
        return *example: `{ 123: {"content": str, "send_at": datetime}, ...}` 
        """
        
        message_dao = BaseDAO(Message, db_session)
        
        messages_chat = await message_dao.get_all_column_values(
            (Message.participant_id, Message.send_at, Message.content),
            Message.chat_id == self.chat_id
        )
        
        return_data = {}
        if messages_chat:
            messages_chat.sort(lambda m: m[1], reverse=True)
        
            for message_pack in messages_chat:
                sender_id = message_pack[0]
                send_at = message_pack[1]
                content = message_pack[2]
                
                return_data[sender_id] = {
                    "content": content,
                    "send_at": send_at,
                }
        return return_data
    
    async def get_or_cache_messages(self):
        pass