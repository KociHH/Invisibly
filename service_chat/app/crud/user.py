import datetime
from fastapi import HTTPException, status
from kos_Htools.redis_core import RedisBase
from kos_Htools.sql.sql_alchemy import BaseDAO
from sqlalchemy import and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from app.db.redis.keys import RedisUserKeysChat, RedisUserKeys
from app.db.sql.models.personal_user import UserChat, Message, ChatParticipant
from shared.config.variables import curretly_msk
from shared.services.tools.other import full_name_constructor
import logging
from shared.crud.sql.user import UserCrudShared
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCrudShared):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class RedisJsonsProcess(RedisUserKeysChat):
    def __init__(
        self, 
        user_id: str | int, 
        chat_id: str | int | None,
        db_session: AsyncSession,
        ):
        super().__init__(chat_id)
        self.user_id = user_id
        self.db_session = db_session
        self.ruk_user = RedisUserKeys(self.user_id)
        self.chatp = ChatsProcess(self.user_id, self.db_session)
     
    def if_not_chat_id(self):
        if not self.chat_id:
            logger.error(f"Не указан атрибут chat_id: {self.chat_id}")
            raise HTTPException(status_code=500, detail="Server error")
        
    async def get_or_cache_participans_chat(self):
        """
        Требования: `self.chat_id`
        
        return: всех участников чата
        """
        self.if_not_chat_id()
        
        chat_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}
        chat_participants: list = chat_data.get("participants", [])
        
        if not chat_participants:
            chat_participans = await self.chatp.chat_parti_dao.get_all_column_values(
                ChatParticipant.user_id,
                ChatParticipant.chat_id == self.chat_id
            )
        
            chat_participants = self.cache_participans_chat(chat_participans, chat_data)
        return chat_participants
    
    def cache_participans_chat(
        self, 
        add_participants: list[str | int], 
        chat_data: dict | None = None
        ):
        """
        Требования: `self.chat_id`
        
        return: всех участников чата
        """
        self.if_not_chat_id()
        
        if not chat_data:
            chat_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}
        
        chat_participants: list = chat_data.get("participants", [])
        for uid in add_participants:
            if uid not in chat_participants:
                chat_participants.append(uid)
        
        self.chat_obj.checkpoint_key.cached(chat_data)
        return chat_participants
        
    def cache_message(
        self,
        message_id: str | int,
        content: str,
        writed_by_id: str | int,
        send_at: datetime.datetime | str,
        created_at: datetime.datetime | str,
        message_data: dict | None = None
    ):
        """
        Требования: `self.chat_id`
        
        Сохраняет либо обновляет сообщение
        
        return: {
            "content": content,
            "writed_by": writed_by,
            "send_at": send_at.isoformat(),
            "created_at": created_at.isoformat()
        } 
        """
        self.if_not_chat_id()
        
        message_id = str(message_id)
        
        if not message_data:
            message_data: dict = self.message_obj.checkpoint_key.get_cached() or {}
        message_data_copy = message_data.copy()
        
        result_message_data = {
            "content": content,
            "writed_by": writed_by_id,
            "send_at": send_at.isoformat(),
            "created_at": created_at.isoformat()
        }
        
        message: dict = message_data_copy.get(message_id, {})
        if message:
            message_data_copy.update(result_message_data)
        else:
            message_data_copy[message_id] = result_message_data
            
        self.message_obj.checkpoint_key.cached(message_data_copy)
        return result_message_data
        
        
    def cache_private_chat(
        self,
        created_at: datetime.datetime | str,
        participant_user_ids: list[str | int],
        private_data: dict | None = None
    ):
        """
        Требования: `self.chat_id`
        
        Сохраняет либо обновляет чат в ключе `info`
        
        return: {
            "chat_id": chat_id,
            "created_at": created_at,   
            "participants": participant_user_ids
        }
        """
        if len(participant_user_ids) < 2:
            logger.error(f"Пользователей в чате {self.chat_id} < 2: {participant_user_ids}")
            raise HTTPException(status_code=500, detail="Server error")
        
        if not private_data:
            private_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}
        private_data_copy = private_data.copy()
        
        result_chat_data = {
            "chat_id": self.chat_id,
            "created_at": created_at.isoformat() if not isinstance(created_at, str) else created_at,   
            "participants": participant_user_ids
        }
        
        if private_data_copy:
            info_chat: dict = private_data_copy.get("info", {})
            if info_chat:
                info_chat.update(result_chat_data)
        else:     
            private_data_copy["info"] = result_chat_data
        
        self.chat_obj.checkpoint_key.cached(private_data_copy)
        return result_chat_data
        
    async def get_or_cache_private_chat(
        self,
        user_id2: int | str,
        ):
        """
        Требования: `self.chat_id`
        
        return: дату чата из ключа
        """
        self.if_not_chat_id()
        
        private_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}
        
        if not private_data:
            chat_data = await self.chatp.create_private_chat(user_id2)
            if chat_data:
                created_at = chat_data.get("created_at")
                participant_user_ids: list = chat_data.get("participants")
        
                private_data = self.cache_private_chat(created_at, participant_user_ids, private_data)
        return private_data

    async def get_or_cache_message(
        self, 
        content: str,
        ):
        """
        Требования: `self.chat_id`
        """
        self.if_not_chat_id()
        
        message_data: dict = self.chat_obj.checkpoint_key.get_cached() or {}
        if not message_data:
            mp = MessageProcess(self.chat_id, self.user_id, self.db_session)
            create = await mp.create_message(content)
            
            if create:
                message_data = self.cache_message(
                   create.message_id,
                   content,
                   create.writed_by,
                   create.send_at,
                   create.created_at,
                   message_data
                )
        return message_data
    
    # UI 
    async def get_or_cache_chats_user(self) -> dict:
        """
        Получает либо cоздает и кеширует `json` чата для отображения под пользователя `self.user_id`
        
        `как будет выглядеть` 
        если написал собеседник:                
            Иван Григорий
            Привет!
            
        если написал от лица самого пользователя:
            Иван Григорий
            вы: Привет!
        
        return *example: {
            chat_id: {
                "content": str, 
                "send_at": datetime,
                "full_name": str,
                "writed_by": str | int,
            },
            ...
        } или {}
        """
        chat_data: dict = self.ruk_user.cached_user_chats_obj.checkpoint_key.get_cached() or {}

        if not chat_data:
            chats = await self.chatp.get_chats_participants_user()

            if chats:
                for chat_id, uids in chats.items():
                    uid2 = uids[1]
                     
                    message = await self.chatp.message_dao.get_one_ordered_or_none(
                        Message.chat_id == chat_id,
                        order_by_clause=desc(Message.message_id)
                    )
                    if not message:
                        continue

                    participant = await self.chatp.get_user_id_from_partid(message.participant_id)
                    if not participant:
                        continue

                    participant_info = await _http_client.get_user_info(uid2)
                    if not participant_info:
                        continue

                    full_name = full_name_constructor(
                        participant_info.get("name"),
                        participant_info.get("surname"),
                        str(uid2)
                    )

                    written_by_current_user: bool = (participant.user_id == self.user_id)

                    chat_data[str(chat_id)] = {
                        "content": message.content,
                        "send_at": message.send_at.isoformat(),
                        "full_name": full_name,
                        "written_by_current_user": written_by_current_user,
                    }

                self.ruk_user.cached_user_chats_obj.checkpoint_key.cached(chat_data)
        return chat_data    

    async def get_or_cache_message_history_private_chat(self) -> dict:
        """
        Требования: `self.chat_id`
        
        Сортирует, кеширует и получает по `json` историю конкретного чата `self.chat_id`
        
        return *example: {
            123: {
                "writed_by": str | int
                "content": str, 
                "send_at": datetime
            }, 
            ...
        } 
        """
        self.if_not_chat_id()
        
        history_data = self.message_obj.checkpoint_key.get_cached()
        if not history_data:
            mp = MessageProcess(self.chat_id, self.user_id, self.db_session)
            
            messages_chat = await mp.message_dao.get_all_column_values(
                (Message.participant_id, Message.send_at, Message.content, Message.message_id),
                Message.chat_id == self.chat_id
            )
        
            return_data = {}
            if messages_chat:
                messages_chat.sort(key=lambda m: m[1], reverse=True)
        
                for message_pack in messages_chat:
                    sender_id = message_pack[0]
                    send_at = message_pack[1]
                    content = message_pack[2]
                    message_id = message_pack[3]
                
                    particant = await self.get_user_id_from_partid(sender_id)
                
                    if particant:
                        return_data[message_id] = {
                            "writed_by": particant.user_id,
                            "content": content,
                            "send_at": send_at.isoformat(),
                        }
        return return_data

    async def delete_chat(self, chat_id: str | int | None = None) -> bool:
        """
        Требования: `self.chat_id`
        
        Удаляет и очищает кеш чата в таблицах `Message`, `UserChat` и связанных с ними таблицах и 
        
        chat_id: id чата
        """
        if chat_id:
            self.chat_id = chat_id
        self.if_not_chat_id()
        
        if isinstance(self.chat_id, str):
            if not self.chat_id.isdigit():
                logger.error(f"Не числовое значение chat_id: {self.chat_id}")
                raise HTTPException(status_code=500, detail="Server error")
                
        chat_id_int = int(self.chat_id)
        
        try:
            await self.chatp.user_chat_dao.delete(UserChat.chat_id == chat_id_int)
            await self.chatp.message_dao.delete(Message.chat_id == chat_id_int)
            
            self.chat_obj.checkpoint_key.delete_key()
            self.message_obj.checkpoint_key.delete_key()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в функции delete_chat: {e}")
            raise HTTPException(status_code=500, detail="Server error")

class ChatsProcess:
    def __init__(
        self, 
        user_id: int | str, 
        db_session: AsyncSession,
        ) -> None:
        self.user_id = user_id
        self.db_session = db_session
        
        self.chat_parti_dao = BaseDAO(ChatParticipant, self.db_session)
        self.user_chat_dao = BaseDAO(UserChat, self.db_session)
        self.message_dao = BaseDAO(Message, self.db_session)

    async def get_user_id_from_partid(self, id: str | int) -> DeclarativeMeta | None:
        particant = await self.chat_parti_dao.get_one(
            ChatParticipant.id == id
        )
        return particant

    async def get_chats_participants_user(self) -> dict:
        """
        Получает все чаты пользователя `self.user_id` и участников
        
        return *example: `{chat_id: [self.user_id, uid2], ...} or {}`
        """
        try:
            user_chats = await self.chat_parti_dao.get_all_column_values(
                ChatParticipant.chat_id,
                ChatParticipant.user_id == self.user_id
            )
        
            result_chat_info = {}
            if user_chats:
                for chat_id in user_chats:
                    user_in_chat: list = await self.chat_parti_dao.get_all_column_values(
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

    async def create_private_chat(self, user_id2: int | str):
        """
        Создает чат в `UserChats` и добавляет пользователей в таблицу `ChatParticipant`
        
        user_id2: собеседник для добавления в чат
        
        return: {
            "chat_id": int,
            "created_at": datetime,
            "participants": [int(self.user_id), int(user_id2)]
        }
        """
        
        created_at = curretly_msk()
        create = await self.user_chat_dao.create({"created_at": created_at})
        if create:
            user_ids = [int(self.user_id), int(user_id2)]
            for uid in user_ids:
                create_particants = await self.chat_parti_dao.create({
                    "chat_id": create.chat_id,
                    "user_id": int(uid),
                })
                
                if not create_particants:
                    logger.error(f"Пользователь {uid} не был добавлен в таблицу ChatParticipant чата: {create.chat_id}")
                    raise HTTPException(status_code=500, detail="Server error")
            
            return {
                "chat_id": create.chat_id,
                "created_at": created_at.isoformat(),
                "participants": user_ids
            }
        else:
            logger.error(f"Новый чат пользователя {self.user_id} не был создан")
            raise HTTPException(status_code=500, detail="Server error")
    
    
class MessageProcess(ChatsProcess):
    def __init__(
        self,
        chat_id: int | str,
        user_id: int | str,
        db_session: AsyncSession
        ):
        self.chat_id = chat_id
        super().__init__(user_id, db_session)
    
    async def create_message(
        self,
        content: str, 
        ):
        """
        return: {
            "message_id": message_id,
            "chat_id": self.chat_id,
            "participant_id": participant_id,
            "content": content,
            "created_at": create_send_at,
            "send_at": create_send_at,
        }
        """
        
        last_message = await self.message_dao.get_one_ordered_or_none(
            Message.chat_id == self.chat_id,
            order_by_clause=desc(Message.message_id),
        )         

        participant_obj = await self.chat_parti_dao.get_one(ChatParticipant.user_id == self.user_id)
        if participant_obj:
            participant_id = participant_obj.id
        else:
            logger.error(f"Не найден user_id в таблице ChatParticipant: {self.user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User in bd not found")

        message_id = last_message.message_id + 1 if last_message else 1
        create_send_at = curretly_msk()

        result_data = {
            "message_id": message_id,
            "chat_id": self.chat_id,
            "participant_id": participant_id,
            "content": content,
            "created_at": create_send_at,
            "send_at": create_send_at,
        }
        return await self.message_dao.create(result_data)