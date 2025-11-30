from app.services.modules.jwt.tasks import CheckJwtTokenDate, CleaningExpiringKeysCache


class JWTService:
    def __init__(self):
        self.check_jwt_token_date = CheckJwtTokenDate()
        self.cleaning_expiring_keys_cache = CleaningExpiringKeysCache()