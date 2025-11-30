from app.services.modules.auth.routes import Login, Register


class AuthService:
    def __init__(self) -> None:
        self.register = Register()
        self.login = Login()