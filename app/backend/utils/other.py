from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from app.backend.data.redis.instance import __redis_save_sql_call__
import logging
import smtplib
from email.message import EmailMessage
import random
from fastapi import Depends
from app.backend.data.redis.utils import RedisJsons, redis_return_data
from app.backend.utils.dependencies import template_not_found_user
from app.backend.utils.user import UserInfo, path_html
from config.env import SMTP_EMAIL, SMTP_HOST, SMTP_PASS, SMTP_PORT

logger = logging.getLogger(__name__)



def send_code_email(
        email_to: str,
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
    msg["To"] = email_to
    msg["Subject"] = "👤 Подтверждение личности"
    msg.set_content(f"""
    Ваш проверочный код {cause}:\n\n
    ++++++++++++++++++\n
    {code}\n
    ++++++++++++++++++\n\n
    """)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.send_message(msg)
        
        logger.info(f"Код подтверждения успешно отправлен на email: {email_to}")
        return {"success": True, "code": code, "message": "Email sent"}
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Ошибка аутентификации SMTP"
        logger.error(f"{error_msg} для email: {email_to}")
        return {"success": False, "error": error_msg}
        
    except smtplib.SMTPRecipientsRefused:
        error_msg = "Email получателя отклонен"
        logger.error(f"{error_msg}: {email_to}")
        return {"success": False, "error": error_msg}
        
    except smtplib.SMTPServerDisconnected:
        error_msg = "Соединение с SMTP сервером разорвано"
        logger.error(f"{error_msg} для email: {email_to}")
        return {"success": False, "error": error_msg}
        
    except smtplib.SMTPException as e:
        error_msg = f"Ошибка SMTP: {str(e)}"
        logger.error(f"{error_msg} для email: {email_to}")
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        logger.error(f"{error_msg} при отправке email на: {email_to}")
        return {"success": False, "error": error_msg}
    
async def short_settings_profile(
        user_info: UserInfo,

        ):
    user_id = user_info.user_id
    rj_edit = RedisJsons(user_id, "edit_profile")

    obj: dict = redis_return_data(items=["name", "login", "bio", "email"], key_data=rj_edit.name_key)
    if obj.get("redis") == "empty":
        user = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
        new_data = rj_edit.save_sql_call("edit_profile", {
            "name": user.get("name"),
            "surname": user.get("surname"),
            "login": user.get("login"),
            "bio": user.get("bio"),
            "email": user.get("email"),
        })
        if not new_data:
            logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
            raise HTTPException(status_code=500, detail="Server error")
        
        obj = new_data

async def full_name_constructor(name: str, surname: str, if_isnone: str) -> str:
    full_name = ""
    if name:
        full_name += name
    if surname and name:
        full_name += f" {surname}"
    else:
        full_name = surname if surname else if_isnone
    return full_name