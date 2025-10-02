from kos_Htools.utils.time import DateTemplate
from passlib.context import CryptContext

def curretly_msk():
    return DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)

path_html = "service_frontend/app/src/html/"

PSWD_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
