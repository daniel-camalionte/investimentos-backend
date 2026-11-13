from pydantic import BaseModel, Field


class HelloResponse(BaseModel):
    message: str = Field(..., examples=["Hello, World!"])
    service: str = Field(..., examples=["investimentos-backend"])
    version: str = Field(..., examples=["0.1.0"])


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str = Field(..., examples=["ok"], description="ok | degraded")
    database: str = Field(..., examples=["ok"], description="ok | unavailable | not_configured")
    service: str
