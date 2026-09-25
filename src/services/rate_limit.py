"""Compatibility wrapper for Redis-backed request limits."""

import redis.asyncio as redis
from fastapi import Request, Response
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from jose import JWTError, jwt

from src.conf.config import settings


async def user_identifier(request: Request) -> str:
    """Use the verified user email as the rate-limit key, falling back to IP."""

    authorization = request.headers.get('authorization', '')
    if authorization.lower().startswith('bearer '):
        token = authorization.split(' ', 1)[1]
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            if payload.get('scope') == 'access_token' and payload.get('sub'):
                return f"user:{payload['sub']}"
        except JWTError:
            pass

    return f"ip:{request.client.host}"


class CompatibleRateLimiter(RateLimiter):
    """Make fastapi-limiter 0.1.6 work with FastAPI's included routers."""

    async def __call__(self, request: Request, response: Response):
        if not FastAPILimiter.redis:
            raise RuntimeError('Rate limiter has not been initialized')

        route_index = 0
        dependency_index = 0
        for index, route in enumerate(request.app.routes):
            if (
                getattr(route, 'path', None) == request.scope['path']
                and request.method in getattr(route, 'methods', set())
            ):
                route_index = index
                for dependency_position, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dependency_index = dependency_position
                        break
                break

        identifier = self.identifier or FastAPILimiter.identifier
        callback = self.callback or FastAPILimiter.http_callback
        rate_key = await identifier(request)
        key = f'{FastAPILimiter.prefix}:{rate_key}:{route_index}:{dependency_index}'
        try:
            pexpire = await self._check(key)
        except redis.exceptions.NoScriptError:
            FastAPILimiter.lua_sha = await FastAPILimiter.redis.script_load(
                FastAPILimiter.lua_script
            )
            pexpire = await self._check(key)

        if pexpire != 0:
            return await callback(request, response, pexpire)
