from app.services.modules.export.routes import CreateUserJWTPost

class ExportService:
    def __init__(self):
        self.create_userJWT_post = CreateUserJWTPost()