
# user: Информация о пользователе в таблице UserRegistered
services_domains_access = {
    "profile": ["user"],
    "settings": ["jwt_confirm_token", "user"],
    "security": ["jwt_confirm_token"],
    "chat": ["chats"],
    "friends": ["friends"],
    "notifications": ["friends", "jwt_confirm_token"],
    "free": ["user"],
    "celery": ["user", "chats", "friends"]
}