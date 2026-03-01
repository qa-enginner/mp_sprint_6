# from sqlalchemy.ext.asyncio import AsyncSession
# from models.entity import User


# async def authenticate_user(session: AsyncSession, username: str, password: str):
#     """Аутентификация пользователя по логину и паролю"""
#     # Ищем пользователя в базе данных по логину
#     result = await session.execute(
#         "SELECT * FROM users WHERE login = :login",
#         {"login": username}
#     )
#     user_row = result.fetchone()
    
#     # Если пользователь не найден, возвращаем None
#     if not user_row:
#         return None
    
#     # Создаем объект пользователя из результата запроса
#     user = User(
#         login=user_row.login,
#         password=user_row.password,
#         first_name=user_row.first_name,
#         last_name=user_row.last_name
#     )
#     user.id = user_row.id
#     user.created_at = user_row.created_at
    
#     # Проверяем пароль
#     if user.check_password(password):
#         return user
#     else:
#         return None