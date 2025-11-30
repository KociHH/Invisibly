from app.services.modules.validation.routes import ConfirmCodeData, ConfirmCodePack, ConfirmPassword, ResendCode

class ValidationService:
    def __init__(self):
        self.confirm_code_data = ConfirmCodeData()
        self.confirm_code = ConfirmCodePack()
        self.confirm_password = ConfirmPassword()
        self.resend_code = ResendCode()