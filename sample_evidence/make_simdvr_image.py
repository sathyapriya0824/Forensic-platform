"""Create a SIMULATED DVR evidence container. NOT a real vendor format."""
import json
import struct
from pathlib import Path

MAGIC = b"SIMDVR01"


def rec(ch, ts, deleted=False):
    return {"channel": ch, "file_ref": f"CH0{ch}_20260929_{ts}.mp4",
            "start": f"2026-09-29 {ts[:2]}:{ts[2:4]}:00",
            "end": f"2026-09-29 {ts[:2]}:{int(ts[2:4]) + 5:02d}:00",
            "timezone": "Asia/Kolkata", "deleted": deleted}


meta = {"format": "SIMDVR", "version": 1, "support_level": "SIMULATED",
        "vendor": "SimDVR", "model": "SIM-8000", "serial": "SIM123456",
        "firmware": "SIM-FW-1.0", "camera_count": 3, "filesystem": "SIMFS",
        "recordings": [rec(1, "0900"), rec(2, "0910"), rec(3, "0920", True)]}
mb = json.dumps(meta, indent=2).encode()
out = Path(__file__).parent / "sample_simdvr.img"
with out.open("wb") as f:
    f.write(MAGIC + struct.pack("<I", len(mb)) + mb)
    f.write(b"\nSIMULATED_VIDEO_DATA\nThis is test evidence only.\n")
print("Created", out, out.stat().st_size, "bytes")
