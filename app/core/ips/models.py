from typing import Optional, List

from pydantic import BaseModel, field_validator

from falcoria_common.schemas.port import Port
from falcoria_common.schemas.ips import BaseIP


class IPAddress(BaseModel):
    ip: Optional[str]


class IP(BaseIP, IPAddress):
    ports: Optional[List[Port]] = []

    @field_validator("hostnames", mode="before")
    def normalize_hostnames(cls, v):
        return v or []
