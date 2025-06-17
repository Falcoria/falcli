from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class ProtocolEnum(str, Enum):
    tcp = "tcp"
    udp = "udp"


class PortState(str, Enum):
    open = "open"
    closed = "closed"
    filtered = "filtered"
    unfiltered = "unfiltered"
    open_filtered = "open|filtered"
    closed_filtered = "closed|filtered"


class Port(BaseModel):
    number: int = Field(ge=0, le=65535)
    protocol: ProtocolEnum
    state: PortState
    reason: Optional[str] = ""
    banner: Optional[str] = ""
    service: Optional[str] = ""
    servicefp: Optional[str] = ""
    scripts: Optional[str] = ""


class IP(BaseModel):
    ip: str
    asnName: Optional[str] = ""
    orgName: Optional[str] = ""
    status: Optional[str] = ""
    os: Optional[str] = ""
    endtime: Optional[int] = 0
    hostnames: Optional[List[str]] = []
    ports: Optional[List[Port]] = []

    @field_validator("hostnames", mode="before")
    def normalize_hostnames(cls, v):
        return v or []
