"""
Создаёт первого администратора. В системе нет self-registration
(ТЗ п.9: доступ по логину и паролю, без сценария саморегистрации) —
первую запись в admins создаёт разработчик, вручную, один раз.

Запуск:
    docker compose exec api sh -c "cd src && python scripts/create_admin.py <username> <password>"
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.api.auth.auth import get_password_hash
from app.db.models.admin import Admin
from app.db.session import AsyncSessionLocal


async def main(username: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Admin).where(Admin.username == username))
        if result.scalar_one_or_none() is not None:
            print(f"Админ '{username}' уже существует")
            return

        admin = Admin(username=username, hashed_password=get_password_hash(password))
        db.add(admin)
        await db.commit()
        print(f"Админ '{username}' создан")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python scripts/create_admin.py <username> <password>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))