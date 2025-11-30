from app.services.modules.notifications.routes import NotificationsFriendsData, NotificationsSystemData


class NotificationsService:
    def __init__(self):
        self.notifications_friends_data = NotificationsFriendsData()
        self.notifications_system_data = NotificationsSystemData()