import hashlib
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


def sha1_hash(password: str) -> str:
    """简单的 SHA1 密码加密函数（毕设项目用）。"""
    return hashlib.sha1(password.encode("utf-8")).hexdigest()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名查询用户，找不到则返回 None。"""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def format_user(user: User) -> Dict[str, Any]:
    """统一返回给上层/接口的用户结构。

    为避免和模型强耦合，这里用 getattr 兼容没有 role/status 字段的情况。
    """
    return {
        "id": getattr(user, "id", None),
        "username": user.username,
        "role": getattr(user, "role", None),
        "status": getattr(user, "status", None),
    }


async def register(
    db: AsyncSession,
    username: str,
    password: str,
    role: Optional[str] = None,
) -> Optional[dict]:
    """用户注册逻辑。

    - username 作为唯一登录名
    - 如果用户已存在，返回 None
    - 成功时返回格式化后的用户信息
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, username)
    if existing_user:
        return None

    # 创建用户，角色/状态可在模型里设置默认值（如 donor / active）
    user = User(
        username=username,
        password_sha1=sha1_hash(password),
        role=role,
    )

    db.add(user)
    try:
        await db.commit()
    except Exception:
        # 出错回滚，抛给上层统一处理
        await db.rollback()
        raise

    await db.refresh(user)
    return format_user(user)


async def login(db: AsyncSession, username: str, password: str) -> Optional[dict]:
    """用户登录逻辑。

    - 用户不存在或密码错误时返回 None
    - 成功时返回格式化后的用户信息
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None

    # 校验密码
    if user.password_sha1 != sha1_hash(password):
        return None

    return format_user(user)