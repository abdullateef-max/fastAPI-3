from fastapi import Request
import logging
from datetime import datetime

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def log_requests(request: Request, call_next):
    # Log the request
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client_host": request.client.host,
        "client_port": request.client.port,
        "headers": dict(request.headers)
    }
    
    logging.info(f"Request: {log_data}")
    
    response = await call_next(request)
    
    response_data = {
        "status_code": response.status_code,
        "headers": dict(response.headers)
    }
    
    logging.info(f"Response: {response_data}")
    
    return response