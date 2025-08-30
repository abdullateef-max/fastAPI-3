from fastapi import Request
from datetime import datetime

# Global request counter
request_count = 0

async def count_requests_middleware(request: Request, call_next):
    global request_count
    request_count += 1
    
    # Log the request
    print(f"Request #{request_count}: {request.method} {request.url} at {datetime.now()}")
    
    response = await call_next(request)
    return response

def get_request_count():
    return request_count