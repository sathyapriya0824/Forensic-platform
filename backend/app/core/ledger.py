"""Hash-chained chain-of-custody ledger (blockchain-INSPIRED, not distributed).
Limitation: someone with full write access could recompute the whole chain.
Mitigation (PLANNED): sign blocks, print head hash in reports, anchor externally."""
import hashlib
import json
import time
from pathlib import Path

GENESIS = "0" * 64
FIELDS = ("index", "timestamp", "action", "data", "prev_hash")


def _block_hash(b: dict) -> str:
    body = json.dumps({k: b[k] for k in FIELDS}, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def blocks(self) -> list:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, action: str, data: dict) -> dict:
        chain = self.blocks()
        b = {
            "index": len(chain),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "action": action,
            "data": data,
            "prev_hash": chain[-1]["hash"] if chain else GENESIS,
        }
        b["hash"] = _block_hash(b)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(b) + "\n")
        return b

    def verify(self) -> dict:
        chain, prev = self.blocks(), GENESIS
        for b in chain:
            if b["prev_hash"] != prev or b["hash"] != _block_hash(b):
                return {"valid": False, "blocks": len(chain),
                        "broken_at": b["index"], "head_hash": prev}
            prev = b["hash"]
        return {"valid": True, "blocks": len(chain), "broken_at": None, "head_hash": prev}
