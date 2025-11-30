from app.services.modules.settings.routes import UserSettingsData, UserLogout

class SettingsService:
    def __init__(self):
        self.user_settings_data = UserSettingsData()
        self.user_logout = UserLogout()