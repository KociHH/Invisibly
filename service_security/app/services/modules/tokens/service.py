from app.services.modules.tokens.routes import RefreshAccessUpdate, AccessUpdate, CheckUpdateTokens, RedisDeleteTokenUser

class TokensService:
    def __init__(self):
        self.refresh_access_update = RefreshAccessUpdate()
        self.access_update = AccessUpdate()
        self.check_update_tokens = CheckUpdateTokens()
        self.redis_delete_token_user = RedisDeleteTokenUser()