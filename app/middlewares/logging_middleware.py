from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
import logging
import uuid # Add uuid import

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        request_id = str(uuid.uuid4())
        client_ip = request.client.host
        logger.info(
            f"REQ_ID: {request_id} - IP: {client_ip} - {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
        return response
