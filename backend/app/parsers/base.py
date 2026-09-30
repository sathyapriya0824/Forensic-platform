"""Vendor parser plugin interface.
support_level must be honest: REAL | SIMULATED | PARTIAL | PLANNED."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DeviceInfo:
    vendor: str
    model: str = "unknown"
    serial: str = "unknown"
    firmware: str = "unknown"
    camera_count: Optional[int] = None
    fs_type: str = "unknown"
    confidence: float = 0.0
    label: str = "PLANNED"


@dataclass
class RecordingEntry:
    channel: int
    file_ref: str
    orig_start: str = ""
    orig_end: str = ""
    orig_tz: str = ""
    size_bytes: int = 0
    is_deleted: bool = False
    extra: dict = field(default_factory=dict)


class VendorParser(ABC):
    name: str = "base"
    support_level: str = "PLANNED"

    @abstractmethod
    def can_parse(self, image_path: str) -> float: ...

    @abstractmethod
    def identify(self, image_path: str) -> DeviceInfo: ...

    @abstractmethod
    def list_recordings(self, image_path: str) -> list[RecordingEntry]: ...

    def extract(self, image_path: str, entry: RecordingEntry, out_path: str) -> bool:
        raise NotImplementedError
