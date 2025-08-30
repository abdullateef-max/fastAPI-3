from fastapi import Request
import time

async def log_middleware(request: Request, call_next):
    # Log IP address and request details
    ip_address = request.client.host
    method = request.method
    url = request.url.path
    
    print(f"Request from IP: {ip_address} - {method} {url}")
    
    # Process the request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"Request completed in {process_time:.2f}s")
    
    return response