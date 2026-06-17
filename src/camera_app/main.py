import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse
from http import HTTPStatus

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl


SERVICE_NAME = os.getenv("SERVICE_NAME", "camera-stream-b2")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.4.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")
MAX_IMAGE_SIZE_MB = float(os.getenv("MAX_IMAGE_SIZE_MB", "5"))


app = FastAPI(
    title="FIT4110 Lab 04 - B2 Camera Stream Service",
    version=SERVICE_VERSION,
    description=(
        "Dockerized service for receiving camera frames and queuing them for "
        "AI vision processing in the Smart Campus B2 scenario."
    ),
)


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int = Field(..., ge=400, le=599)
    detail: str
    instance: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class AnalyzeRequest(BaseModel):
    camera_id: str = Field(..., min_length=3, examples=["cam-gate-01-entry"])
    image_url: HttpUrl = Field(..., examples=["https://example.com/images/frame.jpg"])
    timestamp: datetime = Field(..., examples=["2026-05-22T10:30:00Z"])
    correlationId: str = Field(..., min_length=3, examples=["corr-b2-001-2026"])


class AnalyzeResponseSuccess(BaseModel):
    status: str = Field(..., examples=["received"])
    message: str = Field(..., examples=["Frame queued for async processing."])
    camera_id: str = Field(..., examples=["cam-gate-01-entry"])
    correlationId: str = Field(..., examples=["corr-b2-001-2026"])
    queued_at: str


QUEUED_FRAMES: List[Dict[str, str]] = []


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_problem(
    *,
    status_code: int,
    title: str,
    detail: str,
    instance: Optional[str] = None,
    problem_type: str = "about:blank",
) -> Dict:
    problem = {
        "type": problem_type,
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if instance:
        problem["instance"] = instance
    return problem


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        problem = exc.detail
    else:
        problem = build_problem(
            status_code=exc.status_code,
            title=HTTPStatus(exc.status_code).phrase,
            detail=str(exc.detail),
            instance=str(request.url.path),
        )

    problem.setdefault("status", exc.status_code)
    problem.setdefault("title", HTTPStatus(exc.status_code).phrase)
    problem.setdefault("type", "about:blank")
    problem.setdefault("detail", "Request failed")
    problem.setdefault("instance", str(request.url.path))

    return JSONResponse(
        status_code=exc.status_code,
        content=problem,
        media_type="application/problem+json",
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(item) for item in first_error.get("loc", []))
    message = first_error.get("msg", "Request validation error")
    detail = f"{location}: {message}" if location else message

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=build_problem(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Invalid Request Payload",
            detail=detail,
            instance=str(request.url.path),
            problem_type="https://smart-campus.local/problems/invalid-camera-frame",
        ),
        media_type="application/problem+json",
    )


def verify_bearer_token(authorization: Optional[str] = Header(default=None)) -> None:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=build_problem(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Missing Authorization header",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )

    expected = f"Bearer {AUTH_TOKEN}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=build_problem(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Invalid bearer token",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )


def looks_like_boundary_large_image(image_url: str) -> bool:
    parsed = urlparse(image_url)
    marker = f"{parsed.path} {parsed.query}".lower()
    return "large" in marker or "5mb" in marker or "oversize" in marker


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=now_iso(),
    )


@app.post(
    "/api/v1/vision/analyze",
    response_model=AnalyzeResponseSuccess,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token)],
    responses={
        400: {"model": ProblemDetails},
        401: {"model": ProblemDetails},
        500: {"model": ProblemDetails},
    },
)
def analyze_camera_frame(payload: AnalyzeRequest) -> AnalyzeResponseSuccess:
    image_url = str(payload.image_url)

    if looks_like_boundary_large_image(image_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=build_problem(
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Invalid Request Payload",
                detail=f"Image size must not exceed {MAX_IMAGE_SIZE_MB:g}MB.",
                instance="/api/v1/vision/analyze",
                problem_type="https://smart-campus.local/problems/image-too-large",
            ),
        )

    queued_at = now_iso()
    QUEUED_FRAMES.append(
        {
            "camera_id": payload.camera_id,
            "image_url": image_url,
            "timestamp": payload.timestamp.isoformat(),
            "correlationId": payload.correlationId,
            "queued_at": queued_at,
        }
    )

    return AnalyzeResponseSuccess(
        status="received",
        message="Frame queued for async processing.",
        camera_id=payload.camera_id,
        correlationId=payload.correlationId,
        queued_at=queued_at,
    )
