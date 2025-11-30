from app.services.modules.profile.routes import ProcessingEditProfile, UserEditProfileData, UserProfileData


class ProfileService:
    def __init__(self):
        self.user_profile_data = UserProfileData()
        self.user_edit_profile_data = UserEditProfileData()
        self.processing_edit_profile = ProcessingEditProfile()