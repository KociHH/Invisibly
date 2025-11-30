from app.services.modules.change.routes import ChangeEmail


class ChangeService:
    def __init__(self):
        self.change_email = ChangeEmail()