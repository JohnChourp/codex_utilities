#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path

DEFAULT_REPORT_JSON = str(Path.home() / ".codex" / "tmp" / "crp-frontend-lambda-errors-i18n-report.json")


def main():
    parser = argparse.ArgumentParser(
        description="Fast locale validation from CRP frontend lambda error translation report."
    )
    parser.add_argument(
        "--report-json",
        default=DEFAULT_REPORT_JSON,
    )
    parser.add_argument("--fail-on-missing", action="store_true", default=True)
    parser.add_argument("--no-fail-on-missing", action="store_false", dest="fail_on_missing")
    args = parser.parse_args()

    report_path = Path(args.report_json)
    if not report_path.exists():
        raise SystemExit(f"report not found: {report_path}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = report.get("rows", [])
    unresolved = report.get("unresolved", [])
    el_en_rows = [
        row
        for row in rows
        if str(row.get("language_file", "")).endswith("/el.json")
        or str(row.get("language_file", "")).endswith("/en.json")
    ]
    other_locale_rows = [
        row
        for row in rows
        if row.get("language_file")
        and not (
            str(row.get("language_file", "")).endswith("/el.json")
            or str(row.get("language_file", "")).endswith("/en.json")
        )
    ]

    status_counts = Counter(row.get("status", "") for row in el_en_rows)
    translation_counts = Counter(row.get("translation_status", "") for row in el_en_rows)

    missing_rows = [row for row in el_en_rows if row.get("status") == "missing"]

    output = {
        "report_json": str(report_path),
        "rows_el_en": len(el_en_rows),
        "rows_other_locales": len(other_locale_rows),
        "found": status_counts.get("found", 0),
        "created": status_counts.get("created", 0),
        "missing": status_counts.get("missing", 0),
        "skipped": status_counts.get("skipped", 0),
        "translation_found": translation_counts.get("found", 0),
        "translation_created": translation_counts.get("created", 0),
        "translation_fallback_copied": translation_counts.get("fallback_copied", 0),
        "translation_missing": translation_counts.get("missing", 0),
        "translation_skipped": translation_counts.get("skipped", 0),
        "unresolved_mappings": len(unresolved),
    }
    print(json.dumps(output, ensure_ascii=False))

    if missing_rows:
        print("missing_examples")
        for row in missing_rows[:50]:
            print(
                json.dumps(
                    {
                        "frontend_project": row.get("frontend_project"),
                        "entry_lambda": row.get("entry_lambda"),
                        "error_code": row.get("error_code"),
                        "translation_path": row.get("translation_path"),
                        "language_file": row.get("language_file"),
                    },
                    ensure_ascii=False,
                )
            )

    if args.fail_on_missing and (missing_rows or unresolved or other_locale_rows):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
