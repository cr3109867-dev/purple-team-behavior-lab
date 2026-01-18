from __future__ import annotations
import json, shutil, time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SENSITIVE_DIR = BASE_DIR / "lab_data" / "sensitive_mock"
STAGING_DIR = BASE_DIR / "lab_data" / "staging"
LOG_DIR = BASE_DIR / "lab_data" / "logs"
LOG_FILE = LOG_DIR / "events.jsonl"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_event(event: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"[DEBUG] Evento escrito: {event['event']}")

def main() -> int:
    print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
    print(f"[DEBUG] SENSITIVE_DIR: {SENSITIVE_DIR}")
    print(f"[DEBUG] STAGING_DIR: {STAGING_DIR}")
    print(f"[DEBUG] LOG_FILE: {LOG_FILE}")

    if not SENSITIVE_DIR.exists():
        print(f"[ERROR] No existe: {SENSITIVE_DIR}")
        return 1

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    files = [p for p in SENSITIVE_DIR.iterdir() if p.is_file()]
    print(f"[DEBUG] Archivos encontrados: {[str(p) for p in files]}")

    if not files:
        print(f"[WARN] No hay archivos en: {SENSITIVE_DIR}")
        return 0

    session_id = f"session-{int(time.time())}"

    write_event({
        "ts": utc_now_iso(),
        "session": session_id,
        "event": "SIMULATION_START",
        "details": {"source_dir": str(SENSITIVE_DIR), "staging_dir": str(STAGING_DIR)}
    })

    copied = 0
    for p in files:
        write_event({
            "ts": utc_now_iso(),
            "session": session_id,
            "event": "FILE_ENUM",
            "details": {"path": str(p), "size_bytes": p.stat().st_size}
        })

        time.sleep(0.15)

        dst = STAGING_DIR / p.name
        shutil.copy2(p, dst)
        copied += 1

        write_event({
            "ts": utc_now_iso(),
            "session": session_id,
            "event": "FILE_COPY_TO_STAGING",
            "details": {"src": str(p), "dst": str(dst)}
        })

    write_event({
        "ts": utc_now_iso(),
        "session": session_id,
        "event": "SIMULATION_END",
        "details": {"files_copied": copied}
    })

    print(f"[OK] Simulación completada. Archivos copiados: {copied}")
    print(f"[OK] Log generado: {LOG_FILE}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())