from app.services.modules.chats.routes import UserChatsData, UserChatsWs


class ChatsService:
    def __init__(self) -> None:
        self.user_chats_data = UserChatsData()
        self.user_chats_ws = UserChatsWs()
        
        
        