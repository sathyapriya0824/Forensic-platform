"""SIMDVR parser - ONLY the invented SIMULATED format. NOT a real vendor parser."""
import json
import struct

from .base import DeviceInfo, RecordingEntry, VendorParser

MAGIC = b"SIMDVR01"


class SimDVRParser(VendorParser):
    name = "SimDVR"
    support_level = "SIMULATED"

    def _read_metadata(self, image_path: str) -> dict:
        with open(image_path, "rb") as f:
            if f.read(len(MAGIC)) != MAGIC:
                raise ValueError("Not a SIMDVR image")
            raw_len = f.read(4)
            if len(raw_len) != 4:
                raise ValueError("Invalid SIMDVR metadata length")
            n = struct.unpack("<I", raw_len)[0]
            data = f.read(n)
            if len(data) != n:
                raise ValueError("Incomplete SIMDVR metadata")
            return json.loads(data.decode("utf-8"))

    def can_parse(self, image_path: str) -> float:
        try:
            with open(image_path, "rb") as f:
                return 1.0 if f.read(len(MAGIC)) == MAGIC else 0.0
        except (OSError, TypeError):
            return 0.0

    def identify(self, image_path: str) -> DeviceInfo:
        m = self._read_metadata(image_path)
        return DeviceInfo(
            vendor=m.get("vendor", "SimDVR"), model=m.get("model", "unknown"),
            serial=m.get("serial", "unknown"), firmware=m.get("firmware", "unknown"),
            camera_count=m.get("camera_count"), fs_type=m.get("filesystem", "unknown"),
            confidence=1.0, label="SIMULATED")

    def list_recordings(self, image_path: str) -> list[RecordingEntry]:
        m = self._read_metadata(image_path)
        return [RecordingEntry(
            channel=i.get("channel", 0), file_ref=i.get("file_ref", ""),
            orig_start=i.get("start", ""), orig_end=i.get("end", ""),
            orig_tz=i.get("timezone", ""), is_deleted=i.get("deleted", False))
            for i in m.get("recordings", [])]


parser = SimDVRParser()
