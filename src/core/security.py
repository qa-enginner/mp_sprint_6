# import jwt
# from datetime import datetime, timedelta
# from typing import Optional, Dict, Any
# from jwt import PyJWTError

# from core.config import settings

# # Время жизни токенов
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# REFRESH_TOKEN_EXPIRE_DAYS = 7


# def create_access_token(
#     data: dict,
#     expires_delta: Optional[timedelta] = None
# ) -> str:
#     """Создание access токена"""
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(
#             minutes=ACCESS_TOKEN_EXPIRE_MINUTES
#         )
    
#     to_encode.update({"exp": expire, "type": "access"})
#     encoded_jwt = jwt.encode(
#         to_encode,
#         settings.secret_key,
#         algorithm=settings.algorithm
#     )
#     return encoded_jwt


# def create_refresh_token(
#     data: dict,
#     expires_delta: Optional[timedelta] = None
# ) -> str:
#     """Создание refresh токена"""
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(
#             days=REFRESH_TOKEN_EXPIRE_DAYS
#         )
    
#     to_encode.update({"exp": expire, "type": "refresh"})
#     encoded_jwt = jwt.encode(
#         to_encode,
#         settings.secret_key,
#         algorithm=settings.algorithm
#     )
#     return encoded_jwt


# def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
#     """Проверка валидности access токена"""
#     try:
#         payload = jwt.decode(
#             token,
#             settings.secret_key,
#             algorithms=[settings.algorithm]
#         )
#         token_type = payload.get("type")
#         if token_type != "access":
#             return None
#         return payload
#     except PyJWTError:
#         return None


# def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
#     """Проверка валидности refresh токена"""
#     try:
#         payload = jwt.decode(
#             token,
#             settings.secret_key,
#             algorithms=[settings.algorithm]
#         )
#         token_type = payload.get("type")
#         if token_type != "refresh":
#             return None
#         return payload
#     except PyJWTError:
#         return None


# def add_token_to_blacklist(token: str, redis_client) -> bool:
#     """Добавление токена в черный список (отзыв токена)"""
#     try:
#         payload = jwt.decode(
#             token,
#             settings.secret_key,
#             algorithms=[settings.algorithm]
#         )
#         expires_at = payload.get("exp")
#         if expires_at:
#             # Добавляем токен в Redis с временем жизни до его истечения
#             ttl = expires_at - int(datetime.utcnow().timestamp())
#             if ttl > 0:
#                 redis_client.setex(
#                     f"blacklisted_token:{token}",
#                     ttl,
#                     "true"
#                 )
#                 return True
#         return False
#     except PyJWTError:
#         return False


# def is_token_blacklisted(token: str, redis_client) -> bool:
#     """Проверка, находится ли токен в черном списке"""
#     return redis_client.exists(f"blacklisted_token:{token}") > 0