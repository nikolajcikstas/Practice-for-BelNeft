from fastapi import Header, HTTPException


def get_current_user_id(x_user_id: str = Header(...)) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-User-Id header must be an integer")


def get_current_user_id_optional(x_user_id: str | None = Header(default=None)) -> int | None:
    if x_user_id is None:
        return None
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-User-Id header must be an integer")
