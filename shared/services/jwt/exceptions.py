from fastapi import HTTPException, status

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unable to verify credentials",
    headers={"Authenticate": "Bearer"},
    )