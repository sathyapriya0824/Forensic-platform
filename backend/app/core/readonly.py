"""Software read-only safeguards. NOT a substitute for a hardware write blocker."""
import os
import stat


def lock_readonly(path: str) -> None:
    os.chmod(path, stat.S_IREAD)


def is_readonly(path: str) -> bool:
    return not os.access(path, os.W_OK)


def open_evidence(path: str):
    return open(path, "rb")  # binary read-only, never write
