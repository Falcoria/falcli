from enum import Enum
from uuid import UUID

from typing import Optional, List, Annotated

from pydantic import BaseModel, Field, constr, field_validator, PrivateAttr



class WorkerIP(BaseModel):
    ip: str
    hostname: str
    last_updated: str


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


class Project(BaseModel):
    project_name: str
    id: UUID
    comment: Optional[str] = None
    users: List[str] = Field(default_factory=list)


class ImportMode(str, Enum):
    INSERT = "insert"
    REPLACE = "replace"
    UPDATE = "update"
    APPEND = "append"


class DownloadReportFormat(str, Enum):
    JSON = "json"
    XML = "xml"


class TcpScanType(str, Enum):
    syn = "-sS"
    connect = "-sT"
    ack = "-sA"
    window = "-sW"
    maimon = "-sM"


class TcpStealthScanType(str, Enum):
    null = "-sN"
    fin = "-sF"
    xmas = "-sX"


class TransportProtocol(str, Enum):
    tcp = "tcp"
    udp = "udp"  # maps to -sU


class OpenPortsOpts(BaseModel):
    skip_host_discovery: bool = Field(default=True, description="-Pn")
    dns_resolution: Optional[bool] = Field(default=None, description="-n (False), -R (True)")
    transport_protocol: TransportProtocol = Field(default=TransportProtocol.tcp, description="TCP or UDP")
    max_retries: Optional[int] = Field(default=None, ge=0, le=20, description="--max-retries")
    #min_parallelism: Optional[int] = Field(default=None, ge=1, le=700, description="--min-parallelism")
    #max_parallelism: Optional[int] = Field(default=None, ge=1, le=700, description="--max-parallelism")
    min_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--min-rtt-timeout")
    max_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--max-rtt-timeout")
    initial_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--initial-rtt-timeout")
    min_rate: Optional[int] = Field(default=None, ge=1, le=30000, description="--min-rate")
    max_rate: Optional[int] = Field(default=None, ge=1, le=30000, description="--max-rate")
    #top_ports: Optional[int] = Field(default=None, ge=1, le=5000, description="Top N ports to scan")
    ports: Optional[List[str]] = Field(
        default=None,
        description="List of ports or port ranges (e.g., '22', '80', '1000-2000')"
    )

    def to_nmap_args(self) -> List[str]:
        args = []

        if self.skip_host_discovery:
            args.append("-Pn")
        
        if self.dns_resolution is not None:
            args.append("-R" if self.dns_resolution else "-n")
        
        #if self.tcp_scan_type is not None:
        #    args.append(f"{self.tcp_scan_type.value}")

        if self.transport_protocol == TransportProtocol.udp:
            args.append("-sU")

        if self.max_retries is not None:
            args.append(f"--max-retries {self.max_retries}")

        #if self.host_timeout_ms is not None:
        #    args.append(f"--host-timeout {self.host_timeout_ms}ms")

        #if self.min_parallelism is not None:
        #    args.append(f"--min-parallelism {self.min_parallelism}")

        #if self.max_parallelism is not None:
        #    args.append(f"--max-parallelism {self.max_parallelism}")

        if self.min_rtt_timeout_ms is not None:
            args.append(f"--min-rtt-timeout {self.min_rtt_timeout_ms}ms")

        if self.max_rtt_timeout_ms is not None:
            args.append(f"--max-rtt-timeout {self.max_rtt_timeout_ms}ms")

        if self.initial_rtt_timeout_ms is not None:
            args.append(f"--initial-rtt-timeout {self.initial_rtt_timeout_ms}ms")

        if self.min_rate is not None:
            args.append(f"--min-rate {self.min_rate}")

        if self.max_rate is not None:
            args.append(f"--max-rate {self.max_rate}")
        
        #if self.top_ports is not None:
        #    args.append(f"--top-ports {self.top_ports}")
        
        if self.ports:
            args.append(f"-p {','.join(self.ports)}")

        return args


class ServiceOpts(OpenPortsOpts):
    ports: None = Field(default=None, exclude=True)
    #top_ports: None = Field(default=None, exclude=True)

    aggressive_scan: bool = Field(default=False, description="Enable aggressive scan mode (-A)")
    default_scripts: bool = Field(default=False, description="Use default Nmap scripts (-sC)")
    os_detection: bool = Field(default=False, description="Enable OS detection (-O)")
    traceroute: bool = Field(default=False, description="Trace hop path to each host (--traceroute)")
    _force_service_version: bool = PrivateAttr(default=True)

    def to_nmap_args(self) -> List[str]:
        args = super().to_nmap_args()

        if self.aggressive_scan:
            args.append("-A")
        if self.default_scripts:
            args.append("-sC")
        if self.os_detection:
            args.append("-O")
        if self.traceroute:
            args.append("--traceroute")
        if self._force_service_version:
            args.append("-sV")

        return args


class NmapTask(BaseModel):
    ip: str
    project: UUID
    open_ports_opts: str
    service_opts: str
    timeout: int


HostName = Annotated[
    str,
    constr(
        max_length=253
    )
]


class RunNmapRequest(BaseModel):
    hosts: Optional[List[HostName]] = None
    hosts_file: Optional[str] = Field(default=None, description="Path to file with hosts")

    open_ports_opts: OpenPortsOpts = OpenPortsOpts()
    service_opts: ServiceOpts = ServiceOpts()
    timeout: int = Field(default=1200, ge=1, le=60*60*24, description="Timeout in seconds for the scan")
    include_services: bool = Field(default=True, description="Include service discovery in the scan")
    mode: ImportMode = Field(default=ImportMode.INSERT, description="Import mode for the scan results")
        
    @field_validator('hosts', mode='before')
    def validate_hosts(cls, v, values):
        # If hosts not provided but hosts_file is, will be resolved later in CLI.
        if not v and not values.get("hosts_file"):
            raise ValueError("Either 'hosts' or 'hosts_file' must be provided in the scan config.")
        return v

    def to_nmap_commands(self) -> dict:
        """
        Returns two commands:
        - open_ports_command: initial scan to find open ports
        - service_command: scan to discover services and more details
        """
        open_ports_args = self.open_ports_opts.to_nmap_args()
        service_args = self.service_opts.to_nmap_args()

        hosts = self.hosts or []

        open_ports_command = f"nmap {' '.join(open_ports_args)} {' '.join(hosts)}"
        service_command = f"nmap {' '.join(service_args)} {' '.join(hosts)}"

        return {
            "open_ports_command": open_ports_command,
            "service_command": service_command
        }


class RunNmapWithProject(RunNmapRequest):
    project_id: Optional[str] = Field(
        default=None,
        title="Project ID",
        description="UUID of the project to run the scan on",
        example="123e4567-e89b-12d3-a456-426614174000"
    )