import json
import shutil
import sqlite3
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .core.hashing import hash_file
from .core.ledger import Ledger
from .core.readonly import is_readonly, lock_readonly
from .core.timeutil import normalize
from .parsers.registry import all_parsers, detect, register
from .parsers.simdvr import parser as simdvr_parser

STORAGE = Path(__file__).resolve().parents[1] / "storage"
EVIDENCE_DIR = STORAGE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
DB = STORAGE / "forensics.db"
ledger = Ledger(STORAGE / "ledger.jsonl")

app = FastAPI(title="DVR/NVR Forensic Platform", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"])

register(simdvr_parser)  # SIMULATED only


def db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS evidence"
                "(id TEXT PRIMARY KEY, created TEXT, record TEXT)")
    return con


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/parsers")
def parsers():
    return [{"name": p.name, "support_level": p.support_level} for p in all_parsers()]


@app.post("/api/evidence/upload")
def upload(file: UploadFile = File(...), drift_seconds: int = 0):
    eid = uuid.uuid4().hex[:8]
    safe_name = Path(file.filename or "evidence.img").name
    dest = EVIDENCE_DIR / f"{eid}_{safe_name}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    hashes = hash_file(str(dest))
    lock_readonly(str(dest))

    device, recordings, parser_name, label = None, [], None, "UNKNOWN"
    hit = detect(str(dest))
    if hit:
        p, conf = hit
        parser_name, label = p.name, p.support_level
        device = asdict(p.identify(str(dest)))
        for r in p.list_recordings(str(dest)):
            row = asdict(r)
            row["start_norm"] = normalize(r.orig_start, r.orig_tz, drift_seconds)
            row["end_norm"] = normalize(r.orig_end, r.orig_tz, drift_seconds)
            recordings.append(row)

    record = {"id": eid, "filename": safe_name, "path": str(dest), **hashes,
              "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "parser": parser_name, "support_level": label,
              "readonly": is_readonly(str(dest)), "device": device,
              "recordings": recordings}
    with db() as con:
        con.execute("INSERT INTO evidence VALUES (?,?,?)",
                    (eid, record["uploaded_at"], json.dumps(record)))
    ledger.append("EVIDENCE_ACQUIRED", {
        "evidence_id": eid, "filename": safe_name, "md5": hashes["md5"],
        "sha256": hashes["sha256"], "parser": parser_name, "support_level": label})
    return record


@app.get("/api/evidence")
def list_evidence():
    with db() as con:
        rows = con.execute("SELECT record FROM evidence ORDER BY created DESC").fetchall()
    return [json.loads(r[0]) for r in rows]


@app.get("/api/evidence/{eid}")
def get_evidence(eid: str):
    with db() as con:
        row = con.execute("SELECT record FROM evidence WHERE id=?", (eid,)).fetchone()
    if not row:
        raise HTTPException(404, "Evidence not found")
    return json.loads(row[0])


@app.post("/api/evidence/{eid}/verify")
def verify(eid: str):
    rec = get_evidence(eid)
    now = hash_file(rec["path"])
    ok = now["sha256"] == rec["sha256"] and now["md5"] == rec["md5"]
    ledger.append("INTEGRITY_VERIFIED", {"evidence_id": eid, "match": ok,
                                         "sha256": now["sha256"]})
    return {"evidence_id": eid, "match": ok, "sha256_now": now["sha256"],
            "sha256_original": rec["sha256"]}


@app.get("/api/ledger")
def get_ledger():
    return ledger.blocks()


@app.get("/api/ledger/verify")
def verify_ledger():
    return ledger.verify()
