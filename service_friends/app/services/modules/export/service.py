from app.services.modules.export.routes import FindFriendByParamGet, FriendsRequestsInfoGet, GetFriendInfoGet, GetOrCacheFriendsPatch, UpdateFriendPatch


class ExportService:
    def __init__(self):
        self.find_friend_by_param_get = FindFriendByParamGet()
        self.get_friend_info_get = GetFriendInfoGet()
        self.update_friend_patch = UpdateFriendPatch()
        self.get_or_cache_friends_patch = GetOrCacheFriendsPatch()
        self.friends_requests_info_get = FriendsRequestsInfoGet()