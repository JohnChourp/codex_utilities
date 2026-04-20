#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from shlex import quote


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / '.system' / 'skill-runtime-lib' / 'scripts',
        script_path.parents[2] / 'skill-runtime-lib' / 'scripts',
        script_path.parents[3] / '.system' / 'skill-runtime-lib' / 'scripts',
    ]
    for candidate in candidates:
        if (candidate / 'runtime_support.py').is_file():
            return candidate
    raise SystemExit('Unable to locate shared skill runtime support.')


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _artifact_root() -> Path:
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    return _script_dir() / '.ionic-android-live-serve-inspect' / timestamp


def _report_file() -> Path:
    return _script_dir() / 'report.md'


def _report_text(metadata: dict, artifact_root: Path, report_file: Path) -> str:
    lines = [
        '# ionic-android-live-serve-inspect report',
        '',
        f'- Started (UTC): {metadata["started_at_utc"]}',
        f'- Invoked cwd: {metadata["invocation_cwd"]}',
        f'- Invocation basename: {metadata["invocation_cwd_basename"]}',
        f'- Command: {metadata["command"]}',
        f'- Report file: {report_file}',
        f'- Artifact dir: {artifact_root}',
        '',
        '## Live logs',
        f'[ionic-android-live-serve-inspect] Report file: {report_file}',
    ]
    return '\n'.join(lines) + '\n'


def _bootstrap_run_artifacts(skill_root: Path) -> tuple[Path, Path]:
    artifact_root = _artifact_root()
    artifact_root.mkdir(parents=True, exist_ok=True)

    invocation_cwd_raw = (
        os.environ.get('IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD')
        or os.environ.get('CODEX_SKILL_INVOKED_CWD')
    )
    invocation_cwd = Path(invocation_cwd_raw).expanduser().resolve() if invocation_cwd_raw else Path.cwd().resolve()
    command = ' '.join(quote(arg) for arg in [str(Path(__file__).resolve()), *sys.argv[1:]])
    metadata = {
        'skill': 'ionic-android-live-serve-inspect',
        'skill_root': str(skill_root),
        'invocation_cwd': str(invocation_cwd),
        'invocation_cwd_basename': invocation_cwd.name,
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'command': command,
        'argv': sys.argv[1:],
    }
    report_file = _report_file()
    report_file.parent.mkdir(parents=True, exist_ok=True)
    (artifact_root / 'run.json').write_text(f"{json.dumps(metadata, indent=2)}\n", encoding='utf-8')
    (artifact_root / 'command.txt').write_text(f"{command}\n", encoding='utf-8')
    report_file.write_text(_report_text(metadata, artifact_root, report_file), encoding='utf-8')

    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_RUN_DIR'] = str(artifact_root)
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_RUN_ROOT'] = str(_script_dir())
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD'] = str(invocation_cwd)
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOCATION_BASENAME'] = invocation_cwd.name
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_COMMAND'] = command
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_REPORT_FILE'] = str(report_file)
    os.environ['IONIC_ANDROID_LIVE_SERVE_INSPECT_LATEST_REPORT_FILE'] = str(report_file)
    return artifact_root, report_file


def _report_has_final_summary(report_file: Path) -> bool:
    if not report_file.exists():
        return False
    try:
        return '## Final summary' in report_file.read_text(encoding='utf-8')
    except OSError:
        return False


def _ensure_final_report(report_file: Path, status: int, note: str | None = None) -> None:
    lines = ['','## Final summary', f'- Exit status: {status}']
    if note:
        lines.append(f'- Note: {note}')

    report_file.parent.mkdir(parents=True, exist_ok=True)
    if _report_has_final_summary(report_file):
        return

    final_lines = lines + [
        f'- Report file: {report_file}',
        f'- Command log dir: {report_file.parent}',
    ]
    with report_file.open('a', encoding='utf-8') as handle:
        handle.write('\n'.join(final_lines) + '\n')


def _exit_status_from_system_exit(exc: SystemExit) -> tuple[int, str | None]:
    code = exc.code
    if isinstance(code, int):
        return (code if code != 0 else 1), None
    if isinstance(code, str):
        return 1, code
    return 1, repr(code)


def main(argv: list[str]) -> int:
    skill_root = Path(__file__).resolve().parents[1]
    artifact_root, report_file = _bootstrap_run_artifacts(skill_root)
    print(f'[ionic-android-live-serve-inspect] Report file: {report_file}', flush=True)
    print(f'[ionic-android-live-serve-inspect] Artifact dir: {artifact_root}', flush=True)

    try:
        runtime_support_dir = _runtime_support_dir()
    except SystemExit as exc:
        status, note = _exit_status_from_system_exit(exc)
        if note:
            print(note, file=sys.stderr)
        _ensure_final_report(report_file, status, f'Unable to locate shared skill runtime support: {note or status}')
        return status

    if str(runtime_support_dir) not in sys.path:
        sys.path.insert(0, str(runtime_support_dir))

    from runtime_support import launch_current_skill

    try:
        exit_code = launch_current_skill(Path(__file__).resolve(), argv)
    except KeyboardInterrupt:
        _ensure_final_report(report_file, 130, 'Interrupted before launcher finished')
        return 130
    except SystemExit as exc:
        status, note = _exit_status_from_system_exit(exc)
        if note and status == 1:
            print(note, file=sys.stderr)
        _ensure_final_report(report_file, status, note or 'Launcher raised SystemExit')
        return status
    except Exception as exc:
        note = f'Unhandled error: {exc}'
        print(note, file=sys.stderr)
        _ensure_final_report(report_file, 1, note)
        return 1

    _ensure_final_report(report_file, exit_code, 'Launcher returned')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
