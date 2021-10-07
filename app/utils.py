import asyncio


def io_attempts(num_of_attempts):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < num_of_attempts:
                try:
                    res = await func(*args, **kwargs)
                    return res
                except OSError:
                    await asyncio.sleep(1)
                    attempt += 1
            raise OSError
        return wrapper
    return decorator
