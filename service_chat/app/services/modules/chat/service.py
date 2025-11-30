from service_chat.app.services.modules.chat.routes import UserChatInfo, UserChatHistory, UserSendMessage, UserChatWs


class ChatService:
    def __init__(self) -> None:
        self.user_chat_info = UserChatInfo()
        self.user_chat_history = UserChatHistory()
        self.user_send_message = UserSendMessage()
        self.user_chat_ws = UserChatWs()