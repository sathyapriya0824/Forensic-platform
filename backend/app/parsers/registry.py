from typing import Optional
from .base import VendorParser

_PARSERS: list[VendorParser] = []


def register(parser: VendorParser) -> None:
    _PARSERS.append(parser)


def all_parsers() -> list[VendorParser]:
    return list(_PARSERS)


def detect(image_path: str) -> Optional[tuple[VendorParser, float]]:
    scored = [(p, p.can_parse(image_path)) for p in _PARSERS]
    scored = [s for s in scored if s[1] > 0]
    return max(scored, key=lambda s: s[1]) if scored else None
