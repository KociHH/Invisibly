from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy import and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.redis.create import RedisJsons
from shared.data.redis.instance import __redis_save_chats__
from service_chat.app.db.sql.tables import UserChat, Message
from shared.services.tools.other import full_name_constructor
import logging
from shared.crud.sql.user import UserCRUD
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class ChatsProcess(RedisJsons):
    def __init__(
        self, 
        user_id: int | str, 
        handle: str
        ) -> None:
        super().__init__(user_id, handle)

    async def get_or_cache_chats(
        self, 
        db_session: AsyncSession,
        ) -> dict:
        data: dict | None = __redis_save_chats__.get_cached()

        if not data:
            data = {}

        chat_data = data.get(self.name_key, {})
        if not chat_data:

            chat_dao = BaseDAO(UserChat, db_session)
            message_dao = BaseDAO(Message, db_session)

            chats = await chat_dao.get_all_column_values(
                (UserChat.user1_id, UserChat.user2_id, UserChat.id, UserChat.created_at),
                or_(UserChat.user1_id == self.user_id, UserChat.user2_id == self.user_id)
            )

            if chats:
                chats.sort(lambda f: f[2])
                
                for chat_pack in chats:
                    user1_id = chat_pack[0]
                    user2_id = chat_pack[1]
                    chat_id = chat_pack[2]

                    messages = await message_dao.get_all_column_values(
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

                    full_name = full_name_constructor(chat_user_info.name, chat_user_info.surname)

                    if self.name_key not in data:
                        data[self.name_key] = {}
                        
                    data[self.name_key][id_chat] = {
                        "full_name": full_name,
                        "last_message": last_message,
                        "id_chat": id_chat
                    }

                __redis_save_chats__.cached(data)
            return data.get(self.name_key, {})
            
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
        Return *example: {
            123: {
                "content": str,
                "send_at": datetime,
            },
            345: {
                "content": str,
                "send_at": datetime,
            }
        } 
        """
        
        message_dao = BaseDAO(Message, db_session)
        
        messages_chat = await message_dao.get_all_column_values(
            (Message.sender_id, Message.send_at, Message.content),
            Message.chat_id == self.chat_id
        )
        
        if messages_chat:
            messages_chat.sort(lambda m: m[1], reverse=True)
        
            return_data = {}
            for message_pack in messages_chat:
                sender_id = message_pack[0]
                send_at = message_pack[1]
                content = message_pack[2]
                
                return_data[sender_id] = {
                    "content": content,
                    "send_at": send_at,
                }
            
            return return_data
            
        return {}