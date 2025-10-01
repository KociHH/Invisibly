def full_name_constructor(name: str | None, surname: str | None, if_isnone: str) -> str:
    full_name = ""
    if name:
        full_name += name
    if surname and name:
        full_name += f" {surname}"
    if surname and not name:
        full_name = surname if surname else if_isnone
    return full_name