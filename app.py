"""JMSAR: independently presented 2021 case-study UI backed by the credited SARScope core."""
from __future__ import annotations

import json
import math
import os
import re
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
CORE = "http://127.0.0.1:8765"
YEAR = "2021"
START = "2021-01"
MONTH = re.compile(r"2021-(0[1-9]|1[0-2])\Z")
CASE_ID = re.compile(r"(mannheim|[0-9a-f]{16})\Z")
EXPORT = re.compile(r"[A-Za-z0-9_.-]{1,120}\Z")
app = FastAPI(title="JMSAR 2021 Research Workspace", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=str(ROOT / "web")), name="assets")
_cache: dict[str, tuple[float, dict]] = {}


def core_get(path: str, *, binary: bool = False):
    try:
        with urllib.request.urlopen(CORE + path, timeout=35) as resp:
            body = resp.read(35_000_000)
            return body if binary else json.loads(body)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(503, "SARScope core is unavailable or returned an error: " + str(exc)) from exc


def core_post(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CORE + path, data=data, method="POST",
        headers={"Content-Type": "application/json", "x-sarscope-local": "1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", "replace")
        raise HTTPException(exc.code, detail) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(503, "Local inference service unavailable: " + str(exc)) from exc


def allowed_cases():
    cases = core_get("/api/cases")
    return [c for c in cases if c.get("period") == START]


def checked_case(cid: str):
    if not CASE_ID.fullmatch(cid):
        raise HTTPException(404, "Unknown case")
    if cid not in {c["id"] for c in allowed_cases()}:
        raise HTTPException(404, "JMSAR is restricted to January–December 2021")
    return cid


def get_case(cid: str):
    checked_case(cid)
    cached = _cache.get(cid)
    if cached and time.monotonic() - cached[0] < 180:
        return cached[1]
    data = core_get("/api/cases/" + cid)
    if data.get("spec", {}).get("start_month") != START:
        raise HTTPException(422, "Case lies outside January–December 2021")
    _cache[cid] = (time.monotonic(), data)
    return data


def metrics(data: dict):
    months = data["months"]
    shares = []
    for m in months:
        arr = {int(s["class_id"]): float(s["percent"]) for s in m["shares"]}
        shares.append(arr)
    changes = []
    for idx in range(1, len(shares)):
        # Total variation between class-share vectors. Descriptive, not actual land-cover change.
        tv = sum(abs(shares[idx].get(k, 0) - shares[idx - 1].get(k, 0)) for k in range(9)) / 2
        changes.append({"from": months[idx - 1]["month"], "to": months[idx]["month"], "pp": round(tv, 3)})
    peak = max(changes, key=lambda item: item["pp"]) if changes else None
    aggregate = {k: sum(m.get(k, 0) for m in shares) / len(shares) for k in range(9)}
    top = max(aggregate, key=aggregate.get)
    diversity = []
    for row in shares:
        ps = [max(0.0, row.get(k, 0)) / 100 for k in range(9)]
        diversity.append(-sum(p * math.log(p) for p in ps if p > 0) / math.log(9))
    return {
        "dominant_class_id": top,
        "annual_mean_dominant_share": round(aggregate[top], 2),
        "average_class_mix_diversity": round(sum(diversity) / len(diversity), 3),
        "monthly_mix_shifts": changes,
        "largest_monthly_mix_shift": peak,
        "caution": "Monthly mix shift is computed from predicted class shares, not independently verified ground change.",
    }


@app.get("/")
def index():
    return FileResponse(ROOT / "web/index.html")


@app.get("/api/status")
def status():
    try:
        core = core_get("/api/status")
        cases = allowed_cases()
        return {
            "core_online": True, "ready_for_new_inference": core.get("ready", False),
            "model_present": core.get("model_present", False),
            "credentials_present": core.get("credentials_present", False),
            "years": [YEAR], "months": 12, "saved_cases_2021": len(cases),
            "provenance": "Uses verified SARScope model and processor by Keyur Chaudhari."
        }
    except HTTPException:
        return {
            "core_online": False, "ready_for_new_inference": False,
            "years": [YEAR], "months": 12, "saved_cases_2021": 0,
            "provenance": "SARScope core offline; run SETUP_WINDOWS.cmd then START_JMSAR.cmd."
        }


@app.get("/api/cases")
def cases():
    return allowed_cases()


@app.get("/api/cases/{cid}/summary")
def summary(cid: str):
    data = get_case(cid)
    return {
        "id": cid, "name": data["name"], "spec": data["spec"],
        "classes": data["classes"], "reference": data.get("reference", {}),
        "identity": data.get("identity", {}),
        "months": [
            {"month": m["month"], "shares": m["shares"], "coverage": m["coverage"],
             "radar": m.get("radar", False), "quality": m.get("quality", {})}
            for m in data["months"]
        ],
        "exports": data.get("exports", []),
        "analysis": metrics(data),
    }


@app.get("/api/cases/{cid}/image/{month}/{kind}")
def image(cid: str, month: str, kind: str):
    checked_case(cid)
    if not MONTH.fullmatch(month) or kind not in ("radar", "map"):
        raise HTTPException(404, "Only 2021 image layers are available")
    name = kind + "_" + month + ".png"
    content = core_get("/api/cases/" + cid + "/files/" + name, binary=True)
    return Response(content=content, media_type="image/png",
                    headers={"Cache-Control": "private, max-age=180"})


@app.get("/api/cases/{cid}/export/{filename}")
def export(cid: str, filename: str):
    data = get_case(cid)
    if not EXPORT.fullmatch(filename) or filename not in data.get("exports", []):
        raise HTTPException(404, "Export not in recorded case")
    content = core_get("/api/cases/" + cid + "/files/" + filename, binary=True)
    return Response(
        content=content, media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="' + filename + '"'}
    )


class StudyRequest(BaseModel):
    latitude: float = Field(ge=-79, le=83)
    longitude: float = Field(ge=-179, le=179)
    project: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9:._-]+$")


@app.post("/api/analyze")
def analyze(req: StudyRequest):
    _cache.clear()
    return core_post("/api/analyze", {
        "latitude": req.latitude,
        "longitude": req.longitude,
        "start_month": START,
        "period_mode": "historical",
        "project": req.project
    })


@app.get("/api/jobs/{jid}")
def job(jid: str):
    if not re.fullmatch(r"[0-9a-f]{32}", jid):
        raise HTTPException(404, "Invalid job")
    data = core_get("/api/jobs/" + jid)
    if data.get("state") == "complete":
        _cache.clear()
    return data


if __name__ == "__main__":
    import uvicorn
    threading.Timer(2.0, lambda: webbrowser.open("http://127.0.0.1:8899")).start()
    uvicorn.run(app, host="127.0.0.1", port=8899)
