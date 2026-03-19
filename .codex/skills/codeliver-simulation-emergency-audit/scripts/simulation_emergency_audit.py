#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


SIMULATION_LOG_GROUP = "/aws/lambda/codeliver-group-data-simulation"
APP_SYNC_LOG_GROUP = "/aws/lambda/codeliver-app-sync-actions"
DEFAULT_REGION = "eu-west-1"
DEFAULT_TIMEZONE = "Europe/Athens"
DEFAULT_DEEP_LOOKBACK_HOURS = 0
LOGS_QUERY_LIMIT = 1000
DEFAULT_MODE = "auto"
DEFAULT_LOAD_POLICY = "conservative"
LOAD_POLICIES = ("conservative", "balanced", "aggressive")

TRANSIENT_AWS_ERROR_TOKENS = (
    "throttling",
    "too many requests",
    "requestlimitexceeded",
    "provisionedthroughputexceeded",
    "internalfailure",
    "service unavailable",
    "serviceunavailable",
    "priorrequestnotcomplete",
    "timeout",
)

REASON_FEATURE_NOT_APPLICABLE = "feature_not_applicable"
REASON_THRESHOLD_NOT_REACHED = "threshold_not_reached"
REASON_NO_ELIGIBLE = "no_eligible_off_duty_simulation_driver"
REASON_ATTEMPTED_NOT_PERSISTED = "activation_attempted_but_not_persisted"
REASON_ACTIVATION_DONE = "activation_done"

TERMINAL_BACKLOG_ACTION_TYPES = {
    "request_routed",
    "request_assigned_to_delivery_guy",
    "request_pending",
    "request_completed",
    "request_canceled",
}


@dataclass(frozen=True)
class AnalysisWindow:
    start_ms: int
    end_ms: int
    fetch_start_ms: int
    timezone: str


@dataclass(frozen=True)
class LoadPolicyConfig:
    name: str
    default_request_workers: int
    max_request_workers: int
    soft_exact_request_limit: int
    aws_retry_max_attempts: int
    aws_retry_base_delay_ms: int


@dataclass(frozen=True)
class StageADecision:
    reason_bucket: str
    confidence: str
    is_ambiguous: bool
    short_circuit_reason: str


def _load_policy_config(name: str) -> LoadPolicyConfig:
    normalized = str(name or DEFAULT_LOAD_POLICY).strip().lower()
    if normalized == "aggressive":
        return LoadPolicyConfig(
            name="aggressive",
            default_request_workers=12,
            max_request_workers=24,
            soft_exact_request_limit=1200,
            aws_retry_max_attempts=4,
            aws_retry_base_delay_ms=200,
        )
    if normalized == "balanced":
        return LoadPolicyConfig(
            name="balanced",
            default_request_workers=8,
            max_request_workers=12,
            soft_exact_request_limit=700,
            aws_retry_max_attempts=4,
            aws_retry_base_delay_ms=300,
        )
    return LoadPolicyConfig(
        name="conservative",
        default_request_workers=4,
        max_request_workers=6,
        soft_exact_request_limit=300,
        aws_retry_max_attempts=5,
        aws_retry_base_delay_ms=450,
    )


def _should_retry_aws_error(detail: str) -> bool:
    normalized = str(detail or "").strip().lower()
    if not normalized:
        return False
    return any(token in normalized for token in TRANSIENT_AWS_ERROR_TOKENS)


def _run_command(command: list[str], *, retry_max_attempts: int, retry_base_delay_ms: int) -> str:
    attempts = max(1, int(retry_max_attempts))
    delay_base_s = max(0.05, float(retry_base_delay_ms) / 1000)
    last_exception: subprocess.CalledProcessError | None = None
    for attempt in range(1, attempts + 1):
        try:
            completed = subprocess.run(command, check=True, capture_output=True, text=True)
            return completed.stdout
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip()
            stdout = exc.stdout.strip()
            detail = stderr or stdout or f"exit code {exc.returncode}"
            last_exception = exc
            if attempt >= attempts or not _should_retry_aws_error(detail):
                raise RuntimeError(f"Command failed: {' '.join(command)}\n{detail}") from exc
            sleep_s = delay_base_s * (2 ** (attempt - 1))
            time.sleep(sleep_s)
    if last_exception:
        raise RuntimeError(f"Command failed: {' '.join(command)}\nexit code {last_exception.returncode}") from last_exception
    raise RuntimeError(f"Command failed: {' '.join(command)}")


def _aws_json(command: list[str], *, load_policy: LoadPolicyConfig) -> Any:
    output = _run_command(
        command + ["--output", "json"],
        retry_max_attempts=load_policy.aws_retry_max_attempts,
        retry_base_delay_ms=load_policy.aws_retry_base_delay_ms,
    )
    return json.loads(output)


def _aws_text(command: list[str], *, load_policy: LoadPolicyConfig) -> str:
    return _run_command(
        command + ["--output", "text"],
        retry_max_attempts=load_policy.aws_retry_max_attempts,
        retry_base_delay_ms=load_policy.aws_retry_base_delay_ms,
    ).strip()


def _attr_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"NULL": True}
    if isinstance(value, bool):
        return {"BOOL": value}
    if isinstance(value, int):
        return {"N": str(value)}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Non-finite numeric value: {value}")
        return {"N": str(value)}
    return {"S": str(value)}


def _unmarshal_attr(attribute: dict[str, Any]) -> Any:
    if "S" in attribute:
        return attribute["S"]
    if "N" in attribute:
        raw = attribute["N"]
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw
    if "BOOL" in attribute:
        return bool(attribute["BOOL"])
    if "NULL" in attribute:
        return None
    if "L" in attribute:
        return [_unmarshal_attr(item) for item in attribute["L"]]
    if "M" in attribute:
        return {key: _unmarshal_attr(value) for key, value in attribute["M"].items()}
    return attribute


def unmarshal_item(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if not item:
        return None
    return {key: _unmarshal_attr(value) for key, value in item.items()}


def _dt_to_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _ms_to_local(ms: int, timezone: str) -> str:
    tz = ZoneInfo(timezone)
    return datetime.fromtimestamp(ms / 1000, tz=tz).isoformat()


def _parse_date_boundaries(date_text: str, timezone: str) -> tuple[datetime, datetime]:
    tz = ZoneInfo(timezone)
    day = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=tz)
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = day.replace(hour=23, minute=59, second=59, microsecond=999000)
    return start, end


def _parse_datetime(value: str, timezone: str) -> datetime:
    tz = ZoneInfo(timezone)
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(tz)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def build_analysis_window(args: argparse.Namespace) -> AnalysisWindow:
    if args.date:
        start_dt, end_dt = _parse_date_boundaries(args.date, args.timezone)
    else:
        if not args.from_dt or not args.to_dt:
            raise SystemExit("Provide either --date or both --from and --to.")
        start_dt = _parse_datetime(args.from_dt, args.timezone)
        end_dt = _parse_datetime(args.to_dt, args.timezone)
        if end_dt < start_dt:
            start_dt, end_dt = end_dt, start_dt

    start_ms = _dt_to_ms(start_dt)
    end_ms = _dt_to_ms(end_dt)
    fetch_start_ms = start_ms - max(0, int(args.deep_lookback_hours)) * 60 * 60 * 1000
    return AnalysisWindow(
        start_ms=start_ms,
        end_ms=end_ms,
        fetch_start_ms=fetch_start_ms,
        timezone=args.timezone,
    )


def get_group_settings(group: str, region: str, *, load_policy: LoadPolicyConfig) -> dict[str, Any] | None:
    payload = _aws_json(
        [
            "aws",
            "dynamodb",
            "get-item",
            "--region",
            region,
            "--table-name",
            "codeliver-groups",
            "--key",
            json.dumps({"group": {"S": group}}, separators=(",", ":")),
        ],
        load_policy=load_policy,
    )
    return unmarshal_item(payload.get("Item"))


def query_all(
    *,
    table_name: str,
    region: str,
    key_condition_expression: str,
    expression_attribute_names: dict[str, str],
    expression_attribute_values: dict[str, Any],
    index_name: str | None = None,
    projection_expression: str | None = None,
    consistent_read: bool = False,
    scan_index_forward: bool = True,
    load_policy: LoadPolicyConfig,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    exclusive_start_key: dict[str, Any] | None = None
    marshalled_values = {key: _attr_value(value) for key, value in expression_attribute_values.items()}
    while True:
        command = [
            "aws",
            "dynamodb",
            "query",
            "--region",
            region,
            "--table-name",
            table_name,
            "--key-condition-expression",
            key_condition_expression,
            "--expression-attribute-names",
            json.dumps(expression_attribute_names, separators=(",", ":")),
            "--expression-attribute-values",
            json.dumps(marshalled_values, separators=(",", ":")),
        ]
        if index_name:
            command.extend(["--index-name", index_name])
        if projection_expression:
            command.extend(["--projection-expression", projection_expression])
        if consistent_read:
            command.append("--consistent-read")
        if not scan_index_forward:
            command.extend(["--no-scan-index-forward"])
        if exclusive_start_key:
            command.extend(["--exclusive-start-key", json.dumps(exclusive_start_key, separators=(",", ":"))])
        payload = _aws_json(command, load_policy=load_policy)
        items.extend(unmarshal_item(item) or {} for item in payload.get("Items", []))
        exclusive_start_key = payload.get("LastEvaluatedKey")
        if not exclusive_start_key:
            break
    return items


def get_requests_for_window(group: str, window: AnalysisWindow, region: str, *, load_policy: LoadPolicyConfig) -> list[dict[str, Any]]:
    return query_all(
        table_name="codeliver-requests",
        region=region,
        index_name="group-timestamp-index",
        key_condition_expression="#g = :group AND #ts BETWEEN :from AND :to",
        expression_attribute_names={"#g": "group", "#ts": "timestamp", "#st": "status"},
        expression_attribute_values={":group": group, ":from": str(window.fetch_start_ms), ":to": str(window.end_ms)},
        projection_expression=(
            "request_id, #ts, #st, readyToPickUp, readyToPickUp_timestamp, route_id, "
            "delivery_guy_id, updated_timestamp, canceled_timestamp, completed_timestamp"
        ),
        consistent_read=False,
        scan_index_forward=True,
        load_policy=load_policy,
    )


def get_request_actions(group: str, request_id: str, region: str, *, load_policy: LoadPolicyConfig) -> list[dict[str, Any]]:
    items = query_all(
        table_name="codeliver-requests-actions",
        region=region,
        key_condition_expression="#gr = :group_request_id",
        expression_attribute_names={"#gr": "group_request_id"},
        expression_attribute_values={":group_request_id": f"{group}_{request_id}"},
        scan_index_forward=True,
        load_policy=load_policy,
    )
    items.sort(key=lambda item: safe_timestamp_ms(item.get("timestamp")))
    return items


def get_simulation_delivery_guys(group: str, region: str, *, load_policy: LoadPolicyConfig) -> list[dict[str, Any]]:
    items = query_all(
        table_name="codeliver-delivery-guys",
        region=region,
        key_condition_expression="#g = :group",
        expression_attribute_names={"#g": "group"},
        expression_attribute_values={":group": group},
        consistent_read=True,
        load_policy=load_policy,
    )
    return [item for item in items if item.get("simulation") is True and item.get("delivery_guy_deleted") is not True]


def get_pending_requests_snapshot(group: str, region: str, *, load_policy: LoadPolicyConfig) -> list[dict[str, Any]]:
    items = query_all(
        table_name="codeliver-requests",
        region=region,
        index_name="group-status-index",
        key_condition_expression="#g = :group AND #st = :status",
        expression_attribute_names={"#g": "group", "#st": "status", "#ts": "timestamp"},
        expression_attribute_values={":group": group, ":status": "pending"},
        projection_expression="request_id, #st, readyToPickUp, readyToPickUp_timestamp, route_id, delivery_guy_id, updated_timestamp, #ts",
        consistent_read=False,
        scan_index_forward=True,
        load_policy=load_policy,
    )
    return items


def safe_timestamp_ms(value: Any) -> int:
    def _normalize_epoch(numeric: int) -> int:
        if 1_000_000_000 <= numeric < 1_000_000_000_000:
            return numeric * 1000
        return numeric

    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return _normalize_epoch(int(value))
    raw = str(value).strip()
    if not raw:
        return 0
    try:
        numeric = int(float(raw))
        return _normalize_epoch(numeric)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return 0
        return _dt_to_ms(parsed)


def parse_boolean_token(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    raw = str(value).strip().lower() if value is not None else ""
    if not raw:
        return None
    if raw in {"true", "1", "yes", "y"}:
        return True
    if raw in {"false", "0", "no", "n"}:
        return False
    return None


def resolve_ready_unassigned_reference_ts_ms(request_item: dict[str, Any]) -> int:
    for candidate in (
        request_item.get("readyToPickUp_timestamp"),
        request_item.get("updated_timestamp"),
        request_item.get("timestamp"),
    ):
        ts = safe_timestamp_ms(candidate)
        if ts > 0:
            return ts
    return 0


def is_pending_ready_unassigned_request(request_item: dict[str, Any]) -> bool:
    status = str(request_item.get("status") or "").strip().lower()
    if status != "pending":
        return False
    if parse_boolean_token(request_item.get("readyToPickUp")) is not True:
        return False
    if str(request_item.get("route_id") or "").strip():
        return False
    if str(request_item.get("delivery_guy_id") or "").strip():
        return False
    return True


def build_current_snapshot_counters(
    pending_requests: list[dict[str, Any]],
    *,
    threshold_wait_minutes: int,
    now_ms: int | None = None,
) -> dict[str, int]:
    safe_now_ms = safe_timestamp_ms(now_ms if now_ms is not None else int(time.time() * 1000))
    wait_ms = max(1, int(threshold_wait_minutes)) * 60 * 1000
    counters = {
        "pending_count": 0,
        "unassigned_count": 0,
        "ready_unassigned_count": 0,
        "ready_unassigned_aged_threshold_count": 0,
    }
    for request_item in pending_requests:
        status = str(request_item.get("status") or "").strip().lower()
        if status != "pending":
            continue
        counters["pending_count"] += 1
        is_unassigned = (
            not str(request_item.get("route_id") or "").strip()
            and not str(request_item.get("delivery_guy_id") or "").strip()
        )
        if not is_unassigned:
            continue
        counters["unassigned_count"] += 1
        if parse_boolean_token(request_item.get("readyToPickUp")) is not True:
            continue
        counters["ready_unassigned_count"] += 1
        reference_ts = resolve_ready_unassigned_reference_ts_ms(request_item)
        if reference_ts > 0 and safe_now_ms - reference_ts >= wait_ms:
            counters["ready_unassigned_aged_threshold_count"] += 1
    return counters


def build_effective_group_summary(group_settings: dict[str, Any] | None) -> dict[str, Any]:
    settings = group_settings or {}
    return {
        "group": settings.get("group"),
        "simulation": settings.get("simulation") is True,
        "plan": settings.get("plan"),
        "group_single_store": settings.get("group_single_store") is True,
        "alert_promotion_mode": settings.get("alert_promotion_mode"),
        "default_alert_all_after_alerted_count": settings.get("default_alert_all_after_alerted_count"),
        "notify_all_delivery_guys_in_routes": settings.get("notify_all_delivery_guys_in_routes") is True,
        "emergency_threshold_count": int(settings.get("SIMULATION_EMERGENCY_MIN_READY_UNASSIGNED_COUNT") or 10),
        "emergency_threshold_wait_minutes": int(settings.get("SIMULATION_EMERGENCY_MIN_READY_UNASSIGNED_WAIT_MINUTES") or 15),
    }


def start_logs_query(
    log_group: str,
    query_string: str,
    start_s: int,
    end_s: int,
    region: str,
    *,
    load_policy: LoadPolicyConfig,
) -> str:
    payload = _aws_json(
        [
            "aws",
            "logs",
            "start-query",
            "--region",
            region,
            "--log-group-name",
            log_group,
            "--start-time",
            str(start_s),
            "--end-time",
            str(end_s),
            "--query-string",
            query_string,
        ],
        load_policy=load_policy,
    )
    query_id = payload.get("queryId")
    if not query_id:
        raise RuntimeError(f"CloudWatch start-query returned no queryId for {log_group}")
    return str(query_id)


def poll_logs_query(
    query_id: str,
    region: str,
    *,
    load_policy: LoadPolicyConfig,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    while True:
        payload = _aws_json(
            ["aws", "logs", "get-query-results", "--region", region, "--query-id", query_id],
            load_policy=load_policy,
        )
        status = str(payload.get("status", "")).lower()
        if status == "complete":
            return payload
        if status in {"failed", "cancelled", "timeout", "unknown"}:
            raise RuntimeError(f"CloudWatch query {query_id} ended with status {status}")
        if time.time() >= deadline:
            raise RuntimeError(f"Timed out waiting for CloudWatch query {query_id}")
        time.sleep(1)


def query_logs(
    log_group: str,
    query_string: str,
    window: AnalysisWindow,
    region: str,
    *,
    load_policy: LoadPolicyConfig,
) -> list[dict[str, str]]:
    query_id = start_logs_query(
        log_group,
        query_string,
        window.fetch_start_ms // 1000,
        window.end_ms // 1000,
        region,
        load_policy=load_policy,
    )
    payload = poll_logs_query(query_id, region, load_policy=load_policy)
    results: list[dict[str, str]] = []
    for row in payload.get("results", []):
        mapped = {field["field"]: field.get("value", "") for field in row}
        results.append(mapped)
    return results


def _escape_regex_token(token: str) -> str:
    return re.escape(token)


def collect_log_evidence(group: str, window: AnalysisWindow, region: str, *, load_policy: LoadPolicyConfig) -> dict[str, Any]:
    group_token = _escape_regex_token(group)
    simulation_query = (
        "fields @timestamp, @message "
        f"| filter @message like /{group_token}/ and ("
        "@message like /simulation_emergency_backlog_detected/ or "
        "@message like /simulation_emergency_activation_attempted/ or "
        "@message like /simulation_emergency_activation_skipped/ or "
        "@message like /simulation_emergency_activation_done/ or "
        "@message like /simulation_emergency_release_done/) "
        "| sort @timestamp asc "
        f"| limit {LOGS_QUERY_LIMIT}"
    )
    app_sync_query = (
        "fields @timestamp, @message "
        f"| filter @message like /{group_token}/ and @message like /delivery_guy_status_emergency_activation/ "
        "| sort @timestamp asc "
        f"| limit {LOGS_QUERY_LIMIT}"
    )
    activity_query = (
        "fields @timestamp, @message "
        f"| filter @message like /{group_token}/ "
        "| sort @timestamp asc "
        "| limit 50"
    )
    simulation_rows = query_logs(SIMULATION_LOG_GROUP, simulation_query, window, region, load_policy=load_policy)
    app_sync_rows = query_logs(APP_SYNC_LOG_GROUP, app_sync_query, window, region, load_policy=load_policy)
    activity_rows = query_logs(SIMULATION_LOG_GROUP, activity_query, window, region, load_policy=load_policy)

    def _count(marker: str) -> int:
        return sum(1 for row in simulation_rows if marker in row.get("@message", ""))

    skipped_no_eligible = [
        row for row in simulation_rows
        if "simulation_emergency_activation_skipped" in row.get("@message", "")
        and "no_eligible_off_duty_delivery_guy" in row.get("@message", "")
    ]

    return {
        "simulation_activity_count": len(activity_rows),
        "simulation_rows": simulation_rows,
        "app_sync_rows": app_sync_rows,
        "counts": {
            "backlog_detected": _count("simulation_emergency_backlog_detected"),
            "activation_attempted": _count("simulation_emergency_activation_attempted"),
            "activation_skipped": _count("simulation_emergency_activation_skipped"),
            "activation_done": _count("simulation_emergency_activation_done"),
            "release_done": _count("simulation_emergency_release_done"),
            "app_sync_activation_logs": len(app_sync_rows),
            "activation_skipped_no_eligible": len(skipped_no_eligible),
        },
        "skipped_no_eligible_rows": skipped_no_eligible,
    }


def build_backlog_intervals_for_request(
    request_item: dict[str, Any],
    actions: list[dict[str, Any]],
    threshold_wait_minutes: int,
    analysis_end_ms: int,
) -> list[tuple[int, int, str]]:
    intervals: list[tuple[int, int, str]] = []
    ready_start_ms: int | None = None

    for action in actions:
        action_type = str(action.get("type") or "").strip()
        action_ts = safe_timestamp_ms(action.get("timestamp"))
        if action_ts <= 0:
            continue

        if action_type == "request_ready_to_be_picked_up":
            ready_start_ms = action_ts
            continue

        if action_type in {"request_initialized", "request_pending"}:
            ready_start_ms = None
            continue

        if ready_start_ms is not None and action_type in TERMINAL_BACKLOG_ACTION_TYPES:
            effective_start = ready_start_ms + threshold_wait_minutes * 60 * 1000
            if action_ts > effective_start:
                intervals.append((effective_start, action_ts, str(request_item.get("request_id") or "")))
            ready_start_ms = None

    if ready_start_ms is not None:
        is_still_pending_ready_unassigned = (
            str(request_item.get("status") or "").strip().lower() == "pending"
            and parse_boolean_token(request_item.get("readyToPickUp")) is True
            and not str(request_item.get("route_id") or "").strip()
            and not str(request_item.get("delivery_guy_id") or "").strip()
        )
        if is_still_pending_ready_unassigned:
            effective_start = ready_start_ms + threshold_wait_minutes * 60 * 1000
            if analysis_end_ms > effective_start:
                intervals.append((effective_start, analysis_end_ms, str(request_item.get("request_id") or "")))

    return intervals


def compute_peak(intervals: list[tuple[int, int, str]], analysis_start_ms: int, analysis_end_ms: int) -> dict[str, Any]:
    timeline_events: list[tuple[int, int]] = []
    for start_ms, end_ms, _request_id in intervals:
        clipped_start = max(start_ms, analysis_start_ms)
        clipped_end = min(end_ms, analysis_end_ms)
        if clipped_end <= clipped_start:
            continue
        timeline_events.append((clipped_start, 1))
        timeline_events.append((clipped_end, -1))

    if not timeline_events:
        return {"peak_count": 0, "peak_windows": [], "segments": []}

    timeline_events.sort(key=lambda item: (item[0], item[1]))
    current = 0
    previous_ts: int | None = None
    segments: list[dict[str, int]] = []

    for ts, delta in timeline_events:
        if previous_ts is not None and ts > previous_ts and current > 0:
            segments.append({"start_ms": previous_ts, "end_ms": ts, "count": current})
        current += delta
        previous_ts = ts

    peak_count = max((segment["count"] for segment in segments), default=0)
    peak_windows = [
        {"start_ms": segment["start_ms"], "end_ms": segment["end_ms"], "count": segment["count"]}
        for segment in segments
        if segment["count"] == peak_count
    ]
    return {"peak_count": peak_count, "peak_windows": peak_windows, "segments": segments}


def evaluate_stage_a_decision(
    *,
    group_summary: dict[str, Any],
    snapshot: dict[str, int],
    log_counts: dict[str, int],
) -> StageADecision:
    if not group_summary.get("simulation"):
        return StageADecision(
            reason_bucket=REASON_FEATURE_NOT_APPLICABLE,
            confidence="high",
            is_ambiguous=False,
            short_circuit_reason="group_simulation_disabled",
        )
    if log_counts.get("activation_done", 0) > 0 or log_counts.get("app_sync_activation_logs", 0) > 0:
        return StageADecision(
            reason_bucket=REASON_ACTIVATION_DONE,
            confidence="high",
            is_ambiguous=False,
            short_circuit_reason="activation_logs_present",
        )
    if log_counts.get("activation_skipped_no_eligible", 0) > 0:
        return StageADecision(
            reason_bucket=REASON_NO_ELIGIBLE,
            confidence="high",
            is_ambiguous=False,
            short_circuit_reason="explicit_no_eligible_log",
        )

    threshold = int(group_summary.get("emergency_threshold_count") or 0)
    aged_count = int(snapshot.get("ready_unassigned_aged_threshold_count") or 0)
    has_attempt_logs = (
        int(log_counts.get("backlog_detected", 0)) > 0
        or int(log_counts.get("activation_attempted", 0)) > 0
    )

    if aged_count == 0 and not has_attempt_logs:
        return StageADecision(
            reason_bucket=REASON_THRESHOLD_NOT_REACHED,
            confidence="medium",
            is_ambiguous=False,
            short_circuit_reason="snapshot_aged_ready_unassigned_is_zero",
        )
    if aged_count < threshold and not has_attempt_logs:
        return StageADecision(
            reason_bucket=REASON_THRESHOLD_NOT_REACHED,
            confidence="medium",
            is_ambiguous=False,
            short_circuit_reason="snapshot_aged_ready_unassigned_below_threshold",
        )

    return StageADecision(
        reason_bucket=REASON_ATTEMPTED_NOT_PERSISTED,
        confidence="low",
        is_ambiguous=True,
        short_circuit_reason="stage_a_signals_ambiguous",
    )


def choose_reason_bucket(
    *,
    group_summary: dict[str, Any],
    peak_count: int,
    log_counts: dict[str, int],
    current_eligible_off_duty_count: int,
) -> tuple[str, str]:
    if not group_summary.get("simulation"):
        return REASON_FEATURE_NOT_APPLICABLE, "high"
    if log_counts.get("activation_done", 0) > 0 or log_counts.get("app_sync_activation_logs", 0) > 0:
        return REASON_ACTIVATION_DONE, "high"

    threshold = int(group_summary.get("emergency_threshold_count") or 0)
    if peak_count < threshold:
        return REASON_THRESHOLD_NOT_REACHED, "high"

    if log_counts.get("activation_skipped_no_eligible", 0) > 0:
        return REASON_NO_ELIGIBLE, "high"

    if log_counts.get("backlog_detected", 0) > 0 or log_counts.get("activation_attempted", 0) > 0:
        return REASON_ATTEMPTED_NOT_PERSISTED, "high"

    if current_eligible_off_duty_count == 0:
        return REASON_NO_ELIGIBLE, "medium"

    return REASON_ATTEMPTED_NOT_PERSISTED, "low"


def resolve_request_workers(args: argparse.Namespace, *, load_policy: LoadPolicyConfig, request_count: int) -> int:
    if args.request_workers is not None:
        desired = max(1, int(args.request_workers))
    else:
        desired = load_policy.default_request_workers
    capped = min(desired, load_policy.max_request_workers)
    return max(1, min(capped, max(1, int(request_count))))


def render_text_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    group = report["group"]
    window = report["window"]
    summary = report["group_summary"]
    counts = report["log_evidence"]["counts"]

    lines.append(f"Simulation emergency audit for group `{group}`")
    lines.append(f"Range: {window['start_local']} -> {window['end_local']} ({window['timezone']})")
    lines.append(f"Mode: {report['mode']}")
    lines.append(f"Load policy: {report['load_policy']}")
    lines.append("")
    lines.append("Effective settings:")
    lines.append(f"- simulation: {summary['simulation']}")
    lines.append(f"- plan: {summary.get('plan')}")
    lines.append(f"- group_single_store: {summary.get('group_single_store')}")
    lines.append(f"- emergency threshold count: {summary.get('emergency_threshold_count')}")
    lines.append(f"- emergency threshold wait minutes: {summary.get('emergency_threshold_wait_minutes')}")
    lines.append(f"- alert_promotion_mode: {summary.get('alert_promotion_mode')}")
    lines.append(f"- default_alert_all_after_alerted_count: {summary.get('default_alert_all_after_alerted_count')}")
    lines.append(f"- notify_all_delivery_guys_in_routes: {summary.get('notify_all_delivery_guys_in_routes')}")
    lines.append("")
    snapshot = report.get("current_snapshot", {})
    lines.append("Current snapshot:")
    lines.append(f"- pending_count: {snapshot.get('pending_count', 0)}")
    lines.append(f"- unassigned_count: {snapshot.get('unassigned_count', 0)}")
    lines.append(f"- ready_unassigned_count: {snapshot.get('ready_unassigned_count', 0)}")
    lines.append(f"- ready_unassigned_aged_threshold_count: {snapshot.get('ready_unassigned_aged_threshold_count', 0)}")
    lines.append("")
    lines.append("Verdict:")
    lines.append(f"- reason_bucket: {report['reason_bucket']}")
    lines.append(f"- confidence: {report['reason_bucket_confidence']}")
    lines.append(f"- exact_executed: {report.get('exact_executed', False)}")
    lines.append(f"- short_circuit_reason: {report.get('short_circuit_reason') or 'none'}")
    lines.append(f"- activation_log_count: {counts.get('activation_done', 0)}")
    lines.append(f"- app_sync_activation_logs: {counts.get('app_sync_activation_logs', 0)}")
    lines.append(f"- simulation_activity_count: {report['log_evidence'].get('simulation_activity_count', 0)}")

    if report.get("exact_executed") and "exact" in report:
        exact = report["exact"]
        lines.append("")
        lines.append("Exact backlog analysis:")
        lines.append(f"- request_workers: {exact.get('request_workers', 0)}")
        lines.append(f"- requests_loaded: {exact['requests_loaded']}")
        lines.append(f"- requests_with_actions: {exact['requests_with_actions']}")
        lines.append(f"- eligible_intervals: {exact['eligible_interval_count']}")
        lines.append(f"- peak_backlog_count: {exact['peak_backlog_count']}")
        lines.append(f"- threshold_reached: {exact['threshold_reached']}")
        lines.append(f"- current_eligible_off_duty_simulation_drivers: {exact['current_eligible_off_duty_simulation_drivers']}")
        peak_windows = exact["peak_windows"]
        if peak_windows:
            lines.append("- peak_windows:")
            for window_item in peak_windows[:10]:
                lines.append(
                    "  - "
                    f"{window_item['start_local']} -> {window_item['end_local']} "
                    f"(count={window_item['count']})"
                )
        else:
            lines.append("- peak_windows: none")
        if exact["warnings"]:
            lines.append("- warnings:")
            for warning in exact["warnings"]:
                lines.append(f"  - {warning}")

    lines.append("")
    lines.append("Notes:")
    lines.append("- `alert_promotion_mode` and `default_alert_all_after_alerted_count` affect route alert promotion only.")
    lines.append("- Off-duty -> available emergency activation is driven by `codeliver-group-data-simulation` through `delivery_guy_status_emergency_activation`.")
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    load_policy = _load_policy_config(args.load_policy)
    window = build_analysis_window(args)
    group_settings = get_group_settings(args.group, args.region, load_policy=load_policy)
    group_summary = build_effective_group_summary(group_settings)
    log_evidence = collect_log_evidence(args.group, window, args.region, load_policy=load_policy)
    simulation_delivery_guys = (
        get_simulation_delivery_guys(args.group, args.region, load_policy=load_policy)
        if group_summary["simulation"]
        else []
    )
    current_eligible_off_duty = [
        item for item in simulation_delivery_guys
        if str(item.get("status") or "").strip().lower() == "off_duty"
        and not str(item.get("current_route_id") or "").strip()
        and str(item.get("delivery_guy_id") or "").strip()
        and str(item.get("device_id") or "").strip()
    ]
    pending_requests_snapshot = (
        get_pending_requests_snapshot(args.group, args.region, load_policy=load_policy)
        if group_summary["simulation"]
        else []
    )
    current_snapshot = build_current_snapshot_counters(
        pending_requests_snapshot,
        threshold_wait_minutes=group_summary["emergency_threshold_wait_minutes"],
    )
    stage_a_decision = evaluate_stage_a_decision(
        group_summary=group_summary,
        snapshot=current_snapshot,
        log_counts=log_evidence["counts"],
    )

    report: dict[str, Any] = {
        "group": args.group,
        "mode": args.mode,
        "load_policy": load_policy.name,
        "window": {
            "timezone": args.timezone,
            "start_ms": window.start_ms,
            "end_ms": window.end_ms,
            "fetch_start_ms": window.fetch_start_ms,
            "start_local": _ms_to_local(window.start_ms, args.timezone),
            "end_local": _ms_to_local(window.end_ms, args.timezone),
        },
        "group_summary": group_summary,
        "log_evidence": log_evidence,
        "current_snapshot": current_snapshot,
        "exact_executed": False,
        "short_circuit_reason": None,
    }

    should_run_exact = (
        args.mode == "exact"
        or (args.mode == "auto" and stage_a_decision.is_ambiguous and group_summary["simulation"])
    )
    peak_count = 0
    if should_run_exact and group_summary["simulation"]:
        requests = get_requests_for_window(args.group, window, args.region, load_policy=load_policy)
        threshold_wait_minutes = group_summary["emergency_threshold_wait_minutes"]
        all_intervals: list[tuple[int, int, str]] = []
        requests_with_actions = 0
        warnings: list[str] = []
        request_items_by_id = {
            str(request_item.get("request_id") or "").strip(): request_item
            for request_item in requests
            if str(request_item.get("request_id") or "").strip()
        }
        request_workers = resolve_request_workers(args, load_policy=load_policy, request_count=len(request_items_by_id))
        if len(request_items_by_id) > load_policy.soft_exact_request_limit:
            warnings.append(
                f"large_exact_workload_request_count={len(request_items_by_id)} exceeds soft_limit={load_policy.soft_exact_request_limit}; "
                f"running with capped_workers={request_workers}"
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=request_workers) as executor:
            future_map = {
                executor.submit(get_request_actions, args.group, request_id, args.region, load_policy=load_policy): request_id
                for request_id in request_items_by_id
            }
            for future in concurrent.futures.as_completed(future_map):
                request_id = future_map[future]
                actions = future.result()
                if actions:
                    requests_with_actions += 1
                all_intervals.extend(
                    build_backlog_intervals_for_request(
                        request_item=request_items_by_id[request_id],
                        actions=actions,
                        threshold_wait_minutes=threshold_wait_minutes,
                        analysis_end_ms=window.end_ms,
                    )
                )

        peak = compute_peak(all_intervals, window.start_ms, window.end_ms)
        peak_count = int(peak["peak_count"])
        if args.deep_lookback_hours == 0:
            warnings.append("carry_over_backlog_before_range_not_fully_covered_without_deep_lookback")
        report["exact_executed"] = True
        report["short_circuit_reason"] = None
        report["exact"] = {
            "request_workers": request_workers,
            "requests_loaded": len(requests),
            "requests_with_actions": requests_with_actions,
            "eligible_interval_count": len(all_intervals),
            "peak_backlog_count": peak_count,
            "threshold_reached": peak_count >= group_summary["emergency_threshold_count"],
            "peak_windows": [
                {
                    **segment,
                    "start_local": _ms_to_local(segment["start_ms"], args.timezone),
                    "end_local": _ms_to_local(segment["end_ms"], args.timezone),
                }
                for segment in peak["peak_windows"]
            ],
            "current_simulation_delivery_guys": len(simulation_delivery_guys),
            "current_eligible_off_duty_simulation_drivers": len(current_eligible_off_duty),
            "warnings": warnings,
        }
        reason_bucket, confidence = choose_reason_bucket(
            group_summary=group_summary,
            peak_count=peak_count,
            log_counts=log_evidence["counts"],
            current_eligible_off_duty_count=len(current_eligible_off_duty),
        )
        report["reason_bucket"] = reason_bucket
        report["reason_bucket_confidence"] = confidence
    else:
        report["reason_bucket"] = stage_a_decision.reason_bucket
        report["reason_bucket_confidence"] = stage_a_decision.confidence
        report["short_circuit_reason"] = stage_a_decision.short_circuit_reason
        if args.mode == "quick" and stage_a_decision.is_ambiguous:
            report["short_circuit_reason"] = "quick_mode_stage_a_only_ambiguous"

    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit CodeDeliver simulation emergency congestion for a group.")
    parser.add_argument("group", help="Target group id")
    parser.add_argument("--date", help="Local date in YYYY-MM-DD")
    parser.add_argument("--from", dest="from_dt", help="Local or ISO datetime start")
    parser.add_argument("--to", dest="to_dt", help="Local or ISO datetime end")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE, help="IANA timezone")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--mode", choices=["quick", "exact", "auto"], default=DEFAULT_MODE, help="Analysis mode")
    parser.add_argument(
        "--load-policy",
        choices=list(LOAD_POLICIES),
        default=DEFAULT_LOAD_POLICY,
        help="Concurrency/retry profile used for AWS calls and exact reconstruction",
    )
    parser.add_argument("--deep-lookback-hours", type=int, default=DEFAULT_DEEP_LOOKBACK_HOURS, help="Additional lookback hours for carry-over backlog")
    parser.add_argument(
        "--request-workers",
        type=int,
        default=None,
        help="Parallel workers for per-request action history queries in exact mode (default from load policy)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_report(args)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
