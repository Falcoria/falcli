import re
from enum import Enum
from uuid import UUID
from typing import List, Optional
from typing import Dict

from pydantic import BaseModel, Field, field_validator, PrivateAttr
from pydantic.networks import IPvAnyAddress, IPvAnyNetwork

from app.core.common.enums import ImportMode


class RefusedCounts(BaseModel):
    already_in_scanledger: int = 0
    already_in_queue: int = 0
    forbidden: int = 0
    private_ip: int = 0
    unresolvable: int = 0
    other: int = 0


class ScanStartSummary(BaseModel):
    provided: int
    duplicates_removed: int
    resolved_ips: int
    hostnames_collapsed_to_ip: int
    refused: RefusedCounts
    sent_to_scan: int


class ScanStartResponse(BaseModel):
    summary: ScanStartSummary
    prepared_targets: Dict[str, dict]  # we accept raw dict here (you can refine it later if needed)


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


class CommonScanOpts(BaseModel):
    dns_resolution: Optional[bool] = Field(default=None, description="-n (False), -R (True)")
    max_retries: Optional[int] = Field(default=None, ge=0, le=20, description="--max-retries")
    #min_parallelism: Optional[int] = Field(default=None, ge=1, le=700, description="--min-parallelism")
    #max_parallelism: Optional[int] = Field(default=None, ge=1, le=700, description="--max-parallelism")
    min_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--min-rtt-timeout")
    max_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--max-rtt-timeout")
    initial_rtt_timeout_ms: Optional[int] = Field(default=None, ge=1, le=60000, description="--initial-rtt-timeout")
    min_rate: Optional[int] = Field(default=None, ge=1, le=30000, description="--min-rate")
    max_rate: Optional[int] = Field(default=None, ge=1, le=30000, description="--max-rate")

    def to_nmap_common_args(self) -> List[str]:
        args = []

        if self.dns_resolution is not None:
            args.append("-R" if self.dns_resolution else "-n")

        if self.max_retries is not None:
            args.append(f"--max-retries {self.max_retries}")

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

        return args


class OpenPortsOpts(CommonScanOpts):
    transport_protocol: TransportProtocol = Field(default=TransportProtocol.tcp, description="TCP or UDP")
    ports: List[str] = Field(..., description="List of ports or port ranges (e.g., '22', '80', '1000-2000')")
    skip_host_discovery: bool = Field(default=True, description="-Pn")

    @field_validator("ports")
    @classmethod
    def validate_ports(cls, ports):
        if ports is None:
            return ports
        for port in ports:
            if "-" in port:
                parts = port.split("-")
                if len(parts) != 2 or not all(p.isdigit() for p in parts):
                    raise ValueError(f"Invalid port range format: {port}")
                start, end = map(int, parts)
                if not (1 <= start <= 65535) or start > end:
                    raise ValueError(f"Port range out of bounds: {port}")
            else:
                if not port.isdigit() or not (1 <= int(port) <= 65535):
                    raise ValueError(f"Invalid port: {port}")
        return ports

    def to_nmap_args(self) -> List[str]:
        args = self.to_nmap_common_args()

        if self.transport_protocol == TransportProtocol.udp:
            args.append("-sU")
        
        if self.skip_host_discovery:
            args.append("-Pn")

        if self.ports:
            args.append(f"-p {','.join(self.ports)}")

        return args


class ServiceOpts(CommonScanOpts):
    aggressive_scan: bool = Field(default=False, description="Enable aggressive scan mode (-A)")
    default_scripts: bool = Field(default=False, description="Use default Nmap scripts (-sC)")
    os_detection: bool = Field(default=False, description="Enable OS detection (-O)")
    traceroute: bool = Field(default=False, description="Trace hop path to each host (--traceroute)")

    _transport_protocol: TransportProtocol = PrivateAttr(default=TransportProtocol.tcp)
    _force_service_version: bool = PrivateAttr(default=True)
    _force_skip_host_discovery: bool = PrivateAttr(default=True)
    

    def to_nmap_args(self) -> List[str]:
        args = self.to_nmap_common_args()

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
        if self._transport_protocol == TransportProtocol.udp:
            args.append("-sU")
        if self._force_skip_host_discovery:
            args.append("-Pn")

        return args


class NmapTask(BaseModel):
    ip: str
    hostnames: List[str] = Field(
        default_factory=list,
        description="List of hostnames associated with the target IP"
    )
    project: UUID
    open_ports_opts: str
    service_opts: str
    timeout: int
    include_services: bool
    mode: ImportMode


class RunNmapRequest(BaseModel):
    hosts: List[str]
    open_ports_opts: OpenPortsOpts
    service_opts: ServiceOpts
    timeout: int = Field(..., ge=1, le=60*60*24, description="Timeout in seconds for the scan")
    include_services: bool = Field(..., description="Include service detection in the scan")
    mode: ImportMode = Field(..., description="Import mode for the scan results")
    single_resolve: bool = Field(default=False, description="Resolve hostnames only in one IP")
    track_history: bool = True

    @field_validator('hosts', mode='before')
    @classmethod
    def filter_valid_hosts(cls, hosts: List[str]) -> List[str]:
        validated_hosts = []
        for host in hosts:
            # Check IP
            try:
                IPvAnyAddress(host)
                validated_hosts.append(host)
                continue
            except ValueError:
                pass

            # Check CIDR
            try:
                IPvAnyNetwork(host)
                validated_hosts.append(host)
                continue
            except ValueError:
                pass

            # Check FQDN
            if not re.match(
                r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,63}$',
                host,
                re.IGNORECASE
            ):
                raise ValueError(f'Invalid host format "{host}" — must be IP, CIDR, or FQDN')

            if len(host) > 253:
                raise ValueError('FQDN must be 253 characters or less')

            validated_hosts.append(host)

        return validated_hosts


class RevokeResponse(BaseModel):
    status: str
    revoked: int = 0