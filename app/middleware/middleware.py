import time

from fastapi import Request


async def log_requests(request: Request, call_next):

    start_time = time.time()

    print(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time

    print(f"Response time: {process_time:.4f} seconds")

    response.headers["X-Process-Time"] = str(process_time)

    return response