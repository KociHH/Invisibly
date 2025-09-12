from kos_Htools.utils.time import DateTemplate

ALGORITHM = "HS256"
def curretly_msk():
    return DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)