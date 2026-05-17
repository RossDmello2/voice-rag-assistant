import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_audit")

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # We don't log bodies here to avoid PII, but we log the basics
        path = request.url.path
        method = request.method
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code
        
        audit_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": method,
            "path": path,
            "status_code": status_code,
            "latency_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else "unknown",
        }
        
        logger.info(json.dumps(audit_entry))
        return response
