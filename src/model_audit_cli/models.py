from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints


class SizeScore(BaseModel):
    raspberry_pi: float = Field(..., ge=0, le=1)
    jetson_nano: float = Field(..., ge=0, le=1)
    desktop_pc: float = Field(..., ge=0, le=1)
    aws_server: float = Field(..., ge=0, le=1)


class Metrics(BaseModel):
    name: str
    category: Annotated[str, StringConstraints(pattern="^(MODEL|DATASET|CODE)$")]  # enum-like restriction

    net_score: float = Field(..., ge=0, le=1)
    net_score_latency: int

    ramp_up_time: float = Field(..., ge=0, le=1)
    ramp_up_time_latency: int

    bus_factor: float = Field(..., ge=0, le=1)
    bus_factor_latency: int

    performance_claims: float = Field(..., ge=0, le=1)
    performance_claims_latency: int

    license: float = Field(..., ge=0, le=1)
    license_latency: int

    size_score: SizeScore
    size_score_latency: int

    dataset_and_code_score: float = Field(..., ge=0, le=1)
    dataset_and_code_score_latency: int

    dataset_quality: float = Field(..., ge=0, le=1)
    dataset_quality_latency: int

    code_quality: float = Field(..., ge=0, le=1)
    code_quality_latency: int
