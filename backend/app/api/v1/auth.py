from fastapi import APIRouter, Depends, HTTPException, Body
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.services import auth_service
from app.db.base import get_session as get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
async def register(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    用户注册：
    - username 作为登录名（必填）
    - password 登录密码（必填）
    - role 可选：admin / org / donor，不传默认 donor
    """
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    role = (payload.get("role") or "donor").strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    if role not in {"admin", "org", "donor"}:
        raise HTTPException(status_code=400, detail="角色不合法")

    user = await auth_service.register(db, username=username, password=password, role=role)
    if user is None:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 只返回必要字段，避免把密码哈希带出去
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "role": user.get("role"),
        "status": user.get("status"),
    }


@router.post("/login")
async def login(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录：
    - username + password
    """
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    user = await auth_service.login(db, username=username, password=password)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 后面如果要加 JWT，这里可以一起返回 token
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "role": user.get("role"),
        "status": user.get("status"),
    }
