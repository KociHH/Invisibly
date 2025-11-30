from app.services.modules.export.routes import FindUserByParam, UpdateUser, GetOrCacheUserInfo, GetUserInfo


class ExportService:
    def __init__(self) -> None:
        self.find_user_by_param = FindUserByParam()
        self.update_user = UpdateUser()
        self.get_or_cache_user_info = GetOrCacheUserInfo()
        self.get_user_info = GetUserInfo()