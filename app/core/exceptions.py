from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class FraudDetectionError(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code


async def fraud_detection_exception_handler(request: Request, exc: FraudDetectionError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
