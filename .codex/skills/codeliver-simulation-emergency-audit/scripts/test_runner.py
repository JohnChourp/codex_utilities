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
    build_backlog_intervals_for_request,
    choose_reason_bucket,
    compute_peak,
)


FIXTURES_PATH = Path(__file__).resolve().with_name("fixtures.json")


def load_fixtures() -> dict:
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


class SimulationEmergencyAuditTests(unittest.TestCase):
    maxDiff = None

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


def main(_argv: list[str] | None = None) -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SimulationEmergencyAuditTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

