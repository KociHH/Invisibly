from app.services.modules.friends.routes import ProcessingFriendAdd, ProcessingFriendDelete, UserFriendsData


class FriendsService:
    def __init__(self):
        self.user_friends_data = UserFriendsData()
        self.processing_friend_add = ProcessingFriendAdd()
        self.processing_friend_delete = ProcessingFriendDelete()