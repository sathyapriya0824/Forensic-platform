from app.core.hashing import hash_file
from app.core.ledger import Ledger
from app.core.timeutil import normalize


def test_hash(tmp_path):
    p = tmp_path / "a.bin"; p.write_bytes(b"abc")
    h = hash_file(str(p))
    assert h["md5"] == "900150983cd24fb0d6963f7d28e17f72" and h["size_bytes"] == 3


def test_ledger_tamper(tmp_path):
    l = Ledger(tmp_path / "l.jsonl")
    l.append("A", {"x": 1}); l.append("B", {"x": 2})
    assert l.verify()["valid"]
    t = (tmp_path / "l.jsonl").read_text().replace('"x": 1', '"x": 9')
    (tmp_path / "l.jsonl").write_text(t)
    assert not l.verify()["valid"]


def test_time():
    assert normalize("2026-09-29 09:00:00", "Asia/Kolkata")["utc"] == "2026-09-29T03:30:00Z"
