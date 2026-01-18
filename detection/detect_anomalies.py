#!/usr/bin/env python3
"""
Detector de anomalías para Purple Team Lab.
Funciones:
- Carga y valida eventos desde JSONL
- Aplica reglas de detección:
    * Burst de actividad (muchos eventos en poco tiempo)
    * Copias múltiples a staging
    * Enumeración de archivos sensibles
    * Intentos de acceso a archivos inexistentes
- Genera resumen por tipo de evento
- Exporta alertas a detection/alerts.json
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque, Counter

# --- Configuración ---
BASE_DIR = Path(__file__).resolve().parents[1]
LOG_FILE = BASE_DIR / "lab_data" / "logs" / "events.jsonl"
OUT_FILE = BASE_DIR / "detection" / "alerts.json"

BURST_WINDOW_SECONDS = 3
BURST_EVENT_THRESHOLD = 6
COPY_THRESHOLD = 3
SENSITIVE_KEYWORDS = ["credenciales", "contrato", "historial"]

# --- Funciones auxiliares ---
def parse_ts(ts: str) -> float:
    """Convierte timestamp ISO a segundos."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()

def load_events():
    """Carga eventos desde el archivo JSONL."""
    if not LOG_FILE.exists():
        print(f"[ERROR] No existe el log: {LOG_FILE}")
        return []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def summarize(events):
    """Imprime resumen por tipo de evento."""
    counts = Counter([e["event"] for e in events])
    print("\n[RESUMEN DE EVENTOS]")
    for event_type, count in counts.items():
        print(f"- {event_type}: {count}")

# --- Reglas de detección ---
def detect(events):
    alerts = []
    sessions = defaultdict(list)

    for e in events:
        sessions[e["session"]].append(e)

    for session_id, evts in sessions.items():
        evts.sort(key=lambda e: e["ts"])
        timestamps = [parse_ts(e["ts"]) for e in evts]

        # Regla 1: Burst de actividad
        window = deque()
        for t in timestamps:
            window.append(t)
            while window and t - window[0] > BURST_WINDOW_SECONDS:
                window.popleft()
            if len(window) >= BURST_EVENT_THRESHOLD:
                alerts.append({
                    "session": session_id,
                    "type": "Burst de actividad",
                    "severity": "high",
                    "count": len(window),
                    "ts": evts[0]["ts"]
                })
                break

        # Regla 2: Muchas copias
        copies = [e for e in evts if e["event"] == "FILE_COPY_TO_STAGING"]
        if len(copies) >= COPY_THRESHOLD:
            alerts.append({
                "session": session_id,
                "type": "Muchas copias a staging",
                "severity": "medium",
                "count": len(copies),
                "ts": copies[0]["ts"]
            })

        # Regla 3: Archivos sensibles
        enums = [e for e in evts if e["event"] == "FILE_ENUM"]
        sensitive_hits = [e for e in enums if any(s in e["details"]["path"].lower() for s in SENSITIVE_KEYWORDS)]
        if sensitive_hits:
            alerts.append({
                "session": session_id,
                "type": "Enumeración de archivos sensibles",
                "severity": "low",
                "count": len(sensitive_hits),
                "ts": sensitive_hits[0]["ts"]
            })

        # Regla 4: Acceso a archivos inexistentes
        invalid_access = [e for e in evts if e["event"] == "FILE_ACCESS" and not Path(e["details"]["path"]).exists()]
        if invalid_access:
            alerts.append({
                "session": session_id,
                "type": "Acceso a archivos inexistentes",
                "severity": "medium",
                "count": len(invalid_access),
                "ts": invalid_access[0]["ts"]
            })

    return alerts

# --- Función principal ---
def main():
    print("[INFO] Iniciando análisis de anomalías")

    events = load_events()
    print(f"[INFO] Eventos cargados: {len(events)}")

    if not events:
        print("[INFO] No hay eventos para analizar.")
        return 0

    alerts = detect(events)
    print(f"[INFO] Alertas generadas: {len(alerts)}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)

    if alerts:
        print(f"[OK] Reporte de alertas: {OUT_FILE}")
        for a in alerts:
            print(f"[{a['severity']}] {a['type']} en sesión {a['session']} ({a['count']} eventos)")
    else:
        print("[INFO] No se detectaron anomalías.")

    summarize(events)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())