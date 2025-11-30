from app.services.modules.export.routes import CreatePrivateChatPost, ChatsDeletePost

class ExportService:
    def __init__(self) -> None:
        self.create_private_chat_post = CreatePrivateChatPost()
        self.chats_delete_post = ChatsDeletePost()