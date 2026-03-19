#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from simulation_emergency_audit import (
    REASON_ACTIVATION_DONE,
    REASON_ATTEMPTED_NOT_PERSISTED,
    REASON_NO_ELIGIBLE,
    REASON_THRESHOLD_NOT_REACHED,
    _should_retry_aws_error,
    build_current_snapshot_counters,
    build_backlog_intervals_for_request,
    choose_reason_bucket,
    compute_peak,
    evaluate_stage_a_decision,
)


FIXTURES_PATH = Path(__file__).resolve().with_name("fixtures.json")


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


class SimulationEmergencyAuditTests(unittest.TestCase):
    maxDiff = None

    def test_snapshot_counters_respect_ready_and_wait_gate(self) -> None:
        fixtures = load_fixtures()["snapshot_counters"]
        counters = build_current_snapshot_counters(
            fixtures["pending_requests"],
            threshold_wait_minutes=fixtures["threshold_wait_minutes"],
            now_ms=fixtures["now_ms"],
        )
        self.assertEqual(counters["pending_count"], 4)
        self.assertEqual(counters["unassigned_count"], 4)
        self.assertEqual(counters["ready_unassigned_count"], 2)
        self.assertEqual(counters["ready_unassigned_aged_threshold_count"], 1)

    def test_stage_a_short_circuit_threshold_not_reached_with_zero_ready_aged(self) -> None:
        fixtures = load_fixtures()["stage_a_short_circuit_threshold_not_reached"]
        decision = evaluate_stage_a_decision(
            group_summary=fixtures["group_summary"],
            snapshot=fixtures["snapshot"],
            log_counts=fixtures["log_counts"],
        )
        self.assertEqual(decision.reason_bucket, REASON_THRESHOLD_NOT_REACHED)
        self.assertEqual(decision.confidence, "medium")
        self.assertFalse(decision.is_ambiguous)
        self.assertEqual(decision.short_circuit_reason, "snapshot_aged_ready_unassigned_is_zero")

    def test_stage_a_ambiguous_when_snapshot_or_logs_conflict(self) -> None:
        fixtures = load_fixtures()["stage_a_ambiguous"]
        decision = evaluate_stage_a_decision(
            group_summary=fixtures["group_summary"],
            snapshot=fixtures["snapshot"],
            log_counts=fixtures["log_counts"],
        )
        self.assertEqual(decision.reason_bucket, REASON_ATTEMPTED_NOT_PERSISTED)
        self.assertEqual(decision.confidence, "low")
        self.assertTrue(decision.is_ambiguous)
        self.assertEqual(decision.short_circuit_reason, "stage_a_signals_ambiguous")

    def test_backlog_below_threshold(self) -> None:
        fixtures = load_fixtures()["below_threshold"]
        intervals = build_backlog_intervals_for_request(
            fixtures["request_item"],
            fixtures["actions"],
            fixtures["threshold_wait_minutes"],
            fixtures["analysis_end_ms"],
        )
        peak = compute_peak(intervals, fixtures["analysis_start_ms"], fixtures["analysis_end_ms"])
        self.assertEqual(peak["peak_count"], 1)
        reason, confidence = choose_reason_bucket(
            group_summary=fixtures["group_summary"],
            peak_count=peak["peak_count"],
            log_counts=fixtures["log_counts"],
            current_eligible_off_duty_count=fixtures["current_eligible_off_duty_count"],
        )
        self.assertEqual(reason, REASON_THRESHOLD_NOT_REACHED)
        self.assertEqual(confidence, "high")

    def test_backlog_above_threshold_with_eligible_driver_but_no_persisted_activation(self) -> None:
        fixtures = load_fixtures()["above_threshold_attempted_not_persisted"]
        peak = compute_peak(fixtures["intervals"], fixtures["analysis_start_ms"], fixtures["analysis_end_ms"])
        self.assertEqual(peak["peak_count"], 3)
        reason, confidence = choose_reason_bucket(
            group_summary=fixtures["group_summary"],
            peak_count=peak["peak_count"],
            log_counts=fixtures["log_counts"],
            current_eligible_off_duty_count=fixtures["current_eligible_off_duty_count"],
        )
        self.assertEqual(reason, REASON_ATTEMPTED_NOT_PERSISTED)
        self.assertEqual(confidence, "high")

    def test_backlog_above_threshold_without_eligible_driver(self) -> None:
        fixtures = load_fixtures()["above_threshold_no_eligible"]
        peak = compute_peak(fixtures["intervals"], fixtures["analysis_start_ms"], fixtures["analysis_end_ms"])
        self.assertEqual(peak["peak_count"], 4)
        reason, confidence = choose_reason_bucket(
            group_summary=fixtures["group_summary"],
            peak_count=peak["peak_count"],
            log_counts=fixtures["log_counts"],
            current_eligible_off_duty_count=fixtures["current_eligible_off_duty_count"],
        )
        self.assertEqual(reason, REASON_NO_ELIGIBLE)
        self.assertEqual(confidence, "high")

    def test_activation_done_overrides_other_signals(self) -> None:
        fixtures = load_fixtures()["activation_done"]
        reason, confidence = choose_reason_bucket(
            group_summary=fixtures["group_summary"],
            peak_count=fixtures["peak_count"],
            log_counts=fixtures["log_counts"],
            current_eligible_off_duty_count=fixtures["current_eligible_off_duty_count"],
        )
        self.assertEqual(reason, REASON_ACTIVATION_DONE)
        self.assertEqual(confidence, "high")

    def test_retry_detection_for_transient_aws_errors(self) -> None:
        self.assertTrue(_should_retry_aws_error("ThrottlingException: rate exceeded"))
        self.assertTrue(_should_retry_aws_error("ServiceUnavailable: try again"))
        self.assertFalse(_should_retry_aws_error("ValidationException: bad expression"))


def main(_argv: list[str] | None = None) -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SimulationEmergencyAuditTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
