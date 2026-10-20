"""Strict, bounded evidence evaluation. A declared observation is not verified hardware."""

from __future__ import annotations

import json
import math
import os
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

MAX_BYTES = 2 * 1024 * 1024
MAX_SESSIONS = 500
STAGES = {
    "request",
    "wake_detected",
    "stt_end",
    "intent_end",
    "tts_ready",
    "protocol_end",
    "playback_started",
    "playback_finished",
    "audible_start",
    "error",
}
CHECKS = {"intent_correct", "action_observed", "audible"}
IDENTIFIER = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}\Z")


class InputError(ValueError):
    def __init__(self, code: str, path: str = "$"):
        self.code, self.path = code, path
        super().__init__(code)


def fail(code: str, path: str) -> None:
    raise InputError(code, path)


def strict_object(
    value: Any, required: set[str], optional: set[str], path: str
) -> dict:
    if (
        not isinstance(value, dict)
        or not required <= value.keys()
        or value.keys() - required - optional
    ):
        fail("object_fields", path)
    return value


def identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        fail("identifier", path)
    return value


def number(value: Any, path: str, maximum: float = 43_200_000) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (float, int))
        or not 0 <= value <= maximum
        or not math.isfinite(value)
    ):
        fail("number", path)
    return float(value)


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            fail("duplicate_key", "$")
        out[key] = value
    return out


def load_json(path: str | Path) -> Any:
    """Open a regular file only when atomic no-follow/nonblocking flags exist."""
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not nonblock:
        fail("unsupported_platform", "$")
    flags = os.O_RDONLY | nofollow | nonblock
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                fail("file_size_type", "$")
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            fail("file_size_type", "$")
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda _: fail("number", "$"),
        )
    except InputError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        fail("invalid_file", "$")


def evaluate(data: Any) -> dict:
    root = strict_object(
        data, {"schema", "synthetic", "requirements", "sessions"}, set(), "$"
    )
    if (
        root["schema"] != "assist-scenario-lab/v1"
        or type(root["synthetic"]) is not bool
    ):
        fail("schema", "$")
    requirements = strict_object(
        root["requirements"], set(), CHECKS | {"max_audible_ms"}, "$.requirements"
    )
    for key, value in requirements.items():
        if key == "max_audible_ms":
            number(value, "$.requirements.max_audible_ms")
        elif type(value) is not bool:
            fail("boolean", "$.requirements." + key)
    sessions = root["sessions"]
    if not isinstance(sessions, list) or not 1 <= len(sessions) <= MAX_SESSIONS:
        fail("session_count", "$.sessions")
    results, seen, groups = [], set(), {}
    for i, session in enumerate(sessions):
        path = f"$.sessions[{i}]"
        strict_object(
            session,
            {"id", "platform", "scenario", "clock", "events", "checks"},
            set(),
            path,
        )
        sid = identifier(session["id"], path + ".id")
        platform = identifier(session["platform"], path + ".platform")
        scenario = identifier(session["scenario"], path + ".scenario")
        if sid in seen:
            fail("duplicate_session", path + ".id")
        seen.add(sid)
        clock = session["clock"]
        if clock not in ("relative_monotonic", "utc_derived"):
            fail("clock", path + ".clock")
        events = session["events"]
        if not isinstance(events, list) or not 1 <= len(events) <= len(STAGES):
            fail("event_count", path + ".events")
        times, origins, previous = {}, {}, -1.0
        for j, event in enumerate(events):
            ep = f"{path}.events[{j}]"
            strict_object(event, {"stage", "at_ms", "origin"}, set(), ep)
            stage, origin = event["stage"], event["origin"]
            if not isinstance(stage, str) or stage not in STAGES or stage in times:
                fail("stage", ep)
            if origin not in ("pipeline", "satellite", "operator", "acoustic"):
                fail("origin", ep)
            at = number(event["at_ms"], ep + ".at_ms")
            if at < previous:
                fail("time_order", ep)
            if stage == "audible_start" and origin not in ("operator", "acoustic"):
                fail("audible_origin", ep)
            times[stage], origins[stage], previous = at, origin, at
        if events[0]["stage"] != "request" or times.get("request") != 0:
            fail("request_zero", path + ".events")
        checks = strict_object(session["checks"], CHECKS, set(), path + ".checks")
        normalized = {}
        for name in sorted(CHECKS):
            check = strict_object(
                checks[name], {"result", "method"}, set(), path + ".checks." + name
            )
            result, method = check["result"], check["method"]
            if result not in ("pass", "fail", "unknown"):
                fail("check_result", path + ".checks." + name)
            allowed = (
                {"operator", "ha_state"}
                if name == "action_observed"
                else {"operator", "acoustic"}
                if name == "audible"
                else {"operator", "intent_assertion"}
            )
            if result == "unknown":
                if method != "none":
                    fail("check_method", path + ".checks." + name)
            elif not isinstance(method, str) or method not in allowed:
                fail("check_method", path + ".checks." + name)
            normalized[name] = {"result": result, "method": method}
        if "audible_start" in times and normalized["audible"]["result"] != "pass":
            fail("conflicting_audible", path + ".checks.audible")
        protocol = (
            "fail"
            if "error" in times
            else "pass"
            if "protocol_end" in times
            else "unknown"
        )
        failures, pending = [], []
        if protocol == "fail":
            failures.append("pipeline_error")
        elif protocol == "unknown":
            pending.append("protocol_incomplete")
        for name in sorted(CHECKS):
            if requirements.get(name):
                if normalized[name]["result"] == "fail":
                    failures.append(name)
                elif normalized[name]["result"] == "unknown":
                    pending.append(name)
        audible_ms = times.get("audible_start")
        if "max_audible_ms" in requirements:
            if audible_ms is None:
                pending.append("audible_latency_unknown")
            elif audible_ms > requirements["max_audible_ms"]:
                failures.append("audible_latency_exceeded")
        status = "fail" if failures else "incomplete" if pending else "pass"
        result = {
            "id": sid,
            "platform": platform,
            "scenario": scenario,
            "clock": clock,
            "status": status,
            "protocol": protocol,
            "checks": normalized,
            "failures": failures,
            "pending": pending,
            "request_to_tts_ready_ms": times.get("tts_ready"),
            "request_to_audible_ms": audible_ms,
            "audible_timing_method": origins.get("audible_start"),
        }
        results.append(result)
        key = (platform, scenario, clock, origins.get("audible_start", "none"))
        groups.setdefault(key, []).append(result)
    summary = []
    for key, rows in sorted(groups.items()):
        samples = sorted(
            row["request_to_audible_ms"]
            for row in rows
            if row["request_to_audible_ms"] is not None
        )
        summary.append(
            {
                "platform": key[0],
                "scenario": key[1],
                "clock": key[2],
                "audible_timing_method": key[3],
                "sessions": len(rows),
                "pass": sum(row["status"] == "pass" for row in rows),
                "fail": sum(row["status"] == "fail" for row in rows),
                "incomplete": sum(row["status"] == "incomplete" for row in rows),
                "audible_samples": len(samples),
                "percentile_method": "nearest_rank",
                "p50_audible_ms": samples[math.ceil(len(samples) * 0.5) - 1]
                if samples
                else None,
                "p95_audible_ms": samples[math.ceil(len(samples) * 0.95) - 1]
                if len(samples) >= 20
                else None,
            }
        )
    status = (
        "fail"
        if any(r["status"] == "fail" for r in results)
        else "incomplete"
        if any(r["status"] == "incomplete" for r in results)
        else "pass"
    )
    return {
        "schema": "assist-scenario-lab/report/v1",
        "synthetic": data["synthetic"],
        "evidence_verified": False,
        "status": status,
        "requirements": requirements,
        "sessions": results,
        "groups": summary,
    }


HA_STAGES = {
    "run-start": "request",
    "run-end": "protocol_end",
    "wake_word-end": "wake_detected",
    "stt-end": "stt_end",
    "intent-end": "intent_end",
    "tts-end": "tts_ready",
    "error": "error",
}
HA_IGNORED = {
    "wake_word-start",
    "stt-start",
    "stt-vad-start",
    "stt-vad-end",
    "intent-start",
    "intent-progress",
    "tts-start",
}


def import_ha(
    data: Any, *, session: str, platform: str, synthetic: bool = False
) -> dict:
    """Import one exported run's event array; discard all event data, including audio tokens."""
    identifier(session, "$.session")
    identifier(platform, "$.platform")
    if not isinstance(data, list) or not 1 <= len(data) <= 10_000:
        fail("event_count", "$")
    events, start, previous = [], None, None
    for i, event in enumerate(data):
        strict_object(event, {"type", "timestamp", "data"}, set(), f"$[{i}]")
        typ, timestamp = event["type"], event["timestamp"]
        if (
            not isinstance(typ, str)
            or typ not in HA_STAGES.keys() | HA_IGNORED
            or not isinstance(timestamp, str)
        ):
            fail("ha_event", f"$[{i}]")
        if event["data"] is not None and not isinstance(event["data"], dict):
            fail("ha_event", f"$[{i}]")
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError
        except (ValueError, OverflowError):
            fail("ha_timestamp", f"$[{i}]")
        if previous is not None and dt < previous:
            fail("time_order", f"$[{i}]")
        previous = dt
        if i == 0:
            if typ != "run-start":
                fail("request_zero", "$[0]")
            start = dt
        if typ in HA_STAGES:
            events.append(
                {
                    "stage": HA_STAGES[typ],
                    "at_ms": round((dt - start).total_seconds() * 1000, 3),
                    "origin": "pipeline",
                }
            )
    result = {
        "schema": "assist-scenario-lab/v1",
        "synthetic": synthetic,
        "requirements": {
            "intent_correct": True,
            "action_observed": True,
            "audible": True,
        },
        "sessions": [
            {
                "id": session,
                "platform": platform,
                "scenario": "imported",
                "clock": "utc_derived",
                "events": events,
                "checks": {
                    name: {"result": "unknown", "method": "none"}
                    for name in sorted(CHECKS)
                },
            }
        ],
    }
    evaluate(result)
    return result
