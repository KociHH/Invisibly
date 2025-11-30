from app.services.modules.profile_user.routes import FriendProfileData, ProcessingFriendProfile


class ProfileUserService:
    def __init__(self):
        self.processing_friend_profile = ProcessingFriendProfile()
        self.friend_profile_data = FriendProfileData()
