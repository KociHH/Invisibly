from app.services.modules.security.routes import ChangeEmailData, ProcessingDelete, ProcessingEmail, ProcessingPassword

class SecurityService:
    def __init__(self):
        self.change_email_data = ChangeEmailData()
        self.processing_email = ProcessingEmail()
        self.processing_password = ProcessingPassword()
        self.processing_delete = ProcessingDelete()