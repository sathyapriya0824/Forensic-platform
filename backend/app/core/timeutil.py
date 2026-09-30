"""Timestamp normalization: keep original, convert to UTC, apply DVR clock drift."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def normalize(local_str: str, tz_name: str, drift_seconds: int = 0) -> dict:
    out = {"original": local_str, "timezone": tz_name, "utc": None,
           "drift_seconds": drift_seconds, "note": ""}
    if not local_str:
        out["note"] = "No timestamp available."
        return out
    try:
        naive = datetime.strptime(local_str, "%Y-%m-%d %H:%M:%S")
        try:
            aware = naive.replace(tzinfo=ZoneInfo(tz_name))
        except Exception:
            aware = naive.replace(tzinfo=timezone.utc)
            out["note"] = f"Unknown timezone '{tz_name}', assumed UTC. "
        utc = (aware - timedelta(seconds=drift_seconds)).astimezone(timezone.utc)
        out["utc"] = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        if drift_seconds:
            out["note"] += f"DVR clock was {drift_seconds}s off; corrected."
    except ValueError:
        out["note"] = "Timestamp format not understood."
    return out
