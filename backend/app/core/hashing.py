"""Streaming MD5 + SHA-256 (evidence is never loaded fully into RAM)."""
import hashlib

CHUNK = 1024 * 1024


def hash_file(path: str) -> dict:
    md5, sha, size = hashlib.md5(), hashlib.sha256(), 0
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            md5.update(chunk)
            sha.update(chunk)
            size += len(chunk)
    return {"md5": md5.hexdigest(), "sha256": sha.hexdigest(), "size_bytes": size}


def verify_file(path: str, expected_sha256: str) -> bool:
    return hash_file(path)["sha256"] == expected_sha256
