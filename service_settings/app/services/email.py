from datetime import timedelta
import uuid
from fastapi import HTTPException
from shared.data.redis.instance import __redis_save_sql_call__
import logging
import smtplib
from email.message import EmailMessage
import random
from app.crud.user import RedisJsonsProcess
from app.services.jwt import create_token
from config.env import SMTP_EMAIL, SMTP_HOST, SMTP_PASS, SMTP_PORT
from config.variables import curretly_msk


logger = logging.getLogger(__name__)


class EmailProcess:
    def __init__(
        self,
        email_to: str
    ) -> None:
        self.email_to = email_to
    
    def send_code_email(
        self,
        cause: str,
        size_code: int = 6,
        ) -> dict:
        """
        email_to: На какой адрес почты отправлять

        cause: Причина для отправки
        Предложение: Ваш проверочный код {cause}

        size_code: Сколько цифр будет в коде

        example: (
            email: python@gmail.com
            cause: для смены пароля
            size_code: 6
            )

        return example: (
            {"succsess": True, "code": 123456, "message": "Email sent"} 

            C ошибкой:
            {"succsess": False, "error": "Email получателя отклонен"}
            )
        """

        if size_code <= 2:
            logger.warning(f"Аргумент size_code <= 2. Недопустимо малое число: {size_code}")
            return {"success": False, "error": "Invalid code size"}

        min_code = 10 ** (size_code - 1)
        max_code = (10 ** size_code) - 1
        code = random.randint(min_code, max_code)

        msg = EmailMessage()
        msg["From"] = SMTP_EMAIL
        msg["To"] = self.email_to
        msg["Subject"] = "👤 Подтверждение личности"
        msg.set_content(f"""
        Ваш проверочный код {cause}:\n\n
        + + + + + + + + + + + + + + + + + +\n
        {code}\n
        + + + + + + + + + + + + + + + + + +\n\n
        """)

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASS)
                server.send_message(msg)
        
            logger.info(f"Код подтверждения успешно отправлен на email: {self.email_to}")
            return {"success": True, "code": code, "message": "Email sent"}
        
        except smtplib.SMTPAuthenticationError:
            error_msg = "Ошибка аутентификации SMTP"
            logger.error(f"{error_msg} для email: {self.email_to}")
            return {"success": False, "error": error_msg}
        
        except smtplib.SMTPRecipientsRefused:
            error_msg = "Email получателя отклонен"
            logger.error(f"{error_msg}: {self.email_to}")
            return {"success": False, "error": error_msg}
        
        except smtplib.SMTPServerDisconnected:
            error_msg = "Соединение с SMTP сервером разорвано"
            logger.error(f"{error_msg} для email: {self.email_to}")
            return {"success": False, "error": error_msg}
        
        except smtplib.SMTPException as e:
            error_msg = f"Ошибка SMTP: {str(e)}"
            logger.error(f"{error_msg} для email: {self.email_to}")
            return {"success": False, "error": error_msg}
        
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.error(f"{error_msg} при отправке email на: {self.email_to}")
            return {"success": False, "error": error_msg}

    def send_change_email(
        self,
        rjp: RedisJsonsProcess, 
        user_id: int | str,
        api_type: str
        ):
        """
        rjp: Объект RedisJsonsProcess
        user_id: user_id для сохранения в токен
        api_type: (
                тип запроса, от него зависит возвращаемые данные;
                включенные api_type в функцию: confirm_code, change_email
                )
                
        return: (
            confirm_code: {
                "success": True,
                "message": "Code sent successfully.",
                "token": verification_token,
                "exp_repeated_code_iso": exp_repeated_code_iso,
                "exp_token": exp_token,
                "email": self.email_to,
            }
            
            change_email: {
                "success": True,
                "message": "Verification email sent.",
                "send_for_verification": True
            }
            )
        """
        result_send = self.send_code_email("для подтверждения почты.")
        logger.info(result_send)
        
        if result_send:
            success = result_send.get("success")
            error = result_send.get("error")
            return_data = {}

            if success:
                code: int = result_send.get("code")
                life_time_token = 5
                life_time_repeated_code = 1

                token_data = {
                    "user_id": user_id,
                    "verification_code": code,
                    "new_email": self.email_to,
                    "jti": str(uuid.uuid4()),
                }
                verification_token, _ = create_token(
                    token_data, 
                    timedelta(minutes=life_time_token)
                )
                redis_data = rjp.save_jwt_token(verification_token, life_time_token)

                if not redis_data:
                    logger.error(f'Не получена дата *redis_data при сохранении в redis: {redis_data}')
                    raise HTTPException(status_code=500, detail="Date not received")

                if api_type == "change_email":
                    return_data["success"] = True
                    return_data["message"] = "Verification email sent."
                
                if api_type == "confirm_code":
                    data_token = redis_data.get(rjp.name_key)
                    exp_token = data_token.get("exp")

                    exp_repeated_code = curretly_msk() + timedelta(minutes=life_time_repeated_code)
                    exp_repeated_code_iso = exp_repeated_code.isoformat()

                    return_data = {
                        "success": True,
                        "message": "Code sent successfully.",
                        "token": verification_token,
                        "exp_repeated_code_iso": exp_repeated_code_iso,
                        "exp_token": exp_token,
                        "email": self.email_to,
                        }
                
                return return_data
            else:
                logger.error(f"Произошла ошибка при отправке кода на почту {self.email_to}: {error}")
                raise HTTPException(status_code=500, detail=error)
        else:
            raise HTTPException(status_code=500, detail="The code was not delivered")