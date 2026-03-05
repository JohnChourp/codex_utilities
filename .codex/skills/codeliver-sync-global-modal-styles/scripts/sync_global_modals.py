#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

CLASS_RE = re.compile(r"\.[A-Za-z_][A-Za-z0-9_-]*")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


@dataclass
class RuleBlock:
    start: int
    end: int
    header: str
    text: str
    selectors: Tuple[str, ...]
    context: Tuple[str, ...]


@dataclass
class AtRuleBlock:
    start: int
    end: int
    header: str
    context: Tuple[str, ...]


class ScssParseResult:
    def __init__(self, text: str, rules: List[RuleBlock], at_rules: List[AtRuleBlock]):
        self.text = text
        self.rules = rules
        self.at_rules = at_rules


def strip_comments(value: str) -> str:
    return COMMENT_RE.sub("", value)


def normalize_header(value: str) -> str:
    return " ".join(strip_comments(value).split())


def extract_selectors_from_header(header: str) -> Tuple[str, ...]:
    selectors = sorted(set(CLASS_RE.findall(header)))
    return tuple(selectors)


def parse_scss_blocks(text: str) -> ScssParseResult:
    stack: List[dict] = []
    rules: List[RuleBlock] = []
    at_rules: List[AtRuleBlock] = []

    for idx, ch in enumerate(text):
        if ch == "{":
            j = idx - 1
            while j >= 0 and text[j].isspace():
                j -= 1
            while j >= 0 and text[j] not in "{};":
                j -= 1
            header_start = j + 1
            raw_header = text[header_start:idx]
            header = raw_header.strip()
            if not header:
                continue

            is_at_rule = normalize_header(header).startswith("@")
            at_context = tuple(item["header_norm"] for item in stack if item["type"] == "at")
            entry = {
                "type": "at" if is_at_rule else "rule",
                "header_raw": header,
                "header_norm": normalize_header(header),
                "start": header_start,
                "open": idx,
                "context": at_context,
            }
            stack.append(entry)

        elif ch == "}" and stack:
            entry = stack.pop()
            block_start = entry["start"]
            block_end = idx + 1
            block_text = text[block_start:block_end]
            if entry["type"] == "at":
                at_rules.append(
                    AtRuleBlock(
                        start=block_start,
                        end=block_end,
                        header=entry["header_norm"],
                        context=entry["context"] + (entry["header_norm"],),
                    )
                )
            else:
                selectors = extract_selectors_from_header(entry["header_raw"])
                if selectors:
                    rules.append(
                        RuleBlock(
                            start=block_start,
                            end=block_end,
                            header=entry["header_norm"],
                            text=block_text,
                            selectors=selectors,
                            context=entry["context"],
                        )
                    )

    return ScssParseResult(text=text, rules=rules, at_rules=at_rules)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_panel_from_head(panel_repo: Path) -> str:
    cmd = ["git", "-C", str(panel_repo), "show", "HEAD:src/global.scss"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def all_classes(text: str) -> Set[str]:
    return set(CLASS_RE.findall(text))


def selector_is_modal(selector: str) -> bool:
    return "modal" in selector.lower()


def format_context(context: Tuple[str, ...]) -> str:
    return " > ".join(context) if context else "<top-level>"


def apply_ops(base_text: str, replacements: List[Tuple[int, int, str]], insertions: List[Tuple[int, str]]) -> str:
    out = base_text
    for start, end, new_text in sorted(replacements, key=lambda x: x[0], reverse=True):
        out = out[:start] + new_text + out[end:]
    for pos, new_text in sorted(insertions, key=lambda x: x[0], reverse=True):
        out = out[:pos] + new_text + out[pos:]
    return out


def merge_source_body_with_target_header(target_rule_text: str, source_rule_text: str) -> str:
    t_open = target_rule_text.find("{")
    t_close = target_rule_text.rfind("}")
    s_open = source_rule_text.find("{")
    s_close = source_rule_text.rfind("}")
    if min(t_open, t_close, s_open, s_close) < 0 or t_close <= t_open or s_close <= s_open:
        return source_rule_text
    return (
        target_rule_text[: t_open + 1]
        + source_rule_text[s_open + 1 : s_close]
        + target_rule_text[t_close:]
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sync modal-related global.scss selectors from panel to sap/pos")
    p.add_argument("--mode", choices=["dry-run", "apply"], default="dry-run")
    p.add_argument("--targets", default="sap,pos", help="Comma-separated list: sap,pos")
    p.add_argument("--source", choices=["panel-local", "panel-head"], default="panel-local")
    p.add_argument("--selector-policy", choices=["exact-names"], default="exact-names")
    p.add_argument("--include-utilities", dest="include_utilities", action="store_true")
    p.add_argument("--no-include-utilities", dest="include_utilities", action="store_false")
    p.set_defaults(include_utilities=True)
    p.add_argument("--report", default="./modal-sync-report.json")
    p.add_argument("--codeliver-root", default="/home/dm-soft-1/Downloads/projects/codeliver")
    p.add_argument(
        "--config",
        default=str(Path.home() / ".codex/skills/codeliver-sync-global-modal-styles/references/modal_sync_config.json"),
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    codeliver_root = Path(args.codeliver_root).resolve()
    panel_repo = codeliver_root / "codeliver-panel"
    sap_repo = codeliver_root / "codeliver-sap"
    pos_repo = codeliver_root / "codeliver-pos"

    target_map = {
        "sap": sap_repo / "src/global.scss",
        "pos": pos_repo / "src/global.scss",
    }
    requested_targets = [item.strip() for item in args.targets.split(",") if item.strip()]
    unknown_targets = [t for t in requested_targets if t not in target_map]
    if unknown_targets:
        raise SystemExit(f"Unknown target(s): {', '.join(unknown_targets)}")

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    utilities = set(cfg.get("modal_utilities_allowlist", [])) if args.include_utilities else set()
    allow_insertions_default = bool(cfg.get("allow_insertions", False))

    panel_path = panel_repo / "src/global.scss"
    panel_text = load_panel_from_head(panel_repo) if args.source == "panel-head" else load_text(panel_path)
    panel_parse = parse_scss_blocks(panel_text)

    panel_classes = all_classes(panel_text)
    eligible_selectors = {
        selector for selector in panel_classes if selector_is_modal(selector) or selector in utilities
    }

    report = {
        "mode": args.mode,
        "source": args.source,
        "selector_policy": args.selector_policy,
        "include_utilities": args.include_utilities,
        "eligible_selector_count": len(eligible_selectors),
        "targets": {},
    }

    panel_rule_by_key: Dict[Tuple[Tuple[str, ...], str], RuleBlock] = {}
    panel_conflicts: Set[Tuple[Tuple[str, ...], str]] = set()
    for rule in panel_parse.rules:
        for selector in rule.selectors:
            key = (rule.context, selector)
            prev = panel_rule_by_key.get(key)
            if prev and prev.text != rule.text:
                panel_conflicts.add(key)
            else:
                panel_rule_by_key[key] = rule

    for target in requested_targets:
        target_path = target_map[target]
        target_text = load_text(target_path)
        target_parse = parse_scss_blocks(target_text)
        target_classes = all_classes(target_text)

        sync_selectors = sorted(eligible_selectors.intersection(target_classes))
        sync_set = set(sync_selectors)

        target_conf = cfg.get("targets", {}).get(target, {})
        deny_selectors = set(target_conf.get("deny_selectors", []))
        deny_contexts = set(target_conf.get("deny_contexts", []))
        allow_insertions = bool(target_conf.get("allow_insertions", allow_insertions_default))

        rule_replacements: List[Tuple[int, int, str]] = []
        replacement_records: List[dict] = []
        skipped_records: List[dict] = []
        seen_rule_ids: Set[int] = set()

        for idx, t_rule in enumerate(target_parse.rules):
            shared = [s for s in t_rule.selectors if s in sync_set]
            if not shared:
                continue
            if idx in seen_rule_ids:
                continue

            if any(s in deny_selectors for s in shared):
                skipped_records.append(
                    {
                        "reason": "selector-denylist",
                        "selectors": shared,
                        "context": format_context(t_rule.context),
                    }
                )
                continue

            context_text = format_context(t_rule.context)
            if context_text in deny_contexts:
                skipped_records.append(
                    {
                        "reason": "context-denylist",
                        "selectors": shared,
                        "context": context_text,
                    }
                )
                continue

            candidate_texts = set()
            missing_source = []
            source_keys = []
            for selector in shared:
                key = (t_rule.context, selector)
                if key in panel_conflicts:
                    skipped_records.append(
                        {
                            "reason": "panel-conflict",
                            "selector": selector,
                            "context": context_text,
                        }
                    )
                    continue
                src_rule = panel_rule_by_key.get(key)
                if not src_rule:
                    missing_source.append(selector)
                    continue
                candidate_texts.add(src_rule.text)
                source_keys.append(key)

            if missing_source:
                skipped_records.append(
                    {
                        "reason": "missing-source-context",
                        "selectors": missing_source,
                        "context": context_text,
                    }
                )

            if not candidate_texts:
                continue

            if len(candidate_texts) > 1:
                skipped_records.append(
                    {
                        "reason": "multiple-source-blocks",
                        "selectors": shared,
                        "context": context_text,
                    }
                )
                continue

            source_text = next(iter(candidate_texts))
            new_text = merge_source_body_with_target_header(t_rule.text, source_text)
            if new_text == t_rule.text:
                continue

            seen_rule_ids.add(idx)
            rule_replacements.append((t_rule.start, t_rule.end, new_text))
            replacement_records.append(
                {
                    "selectors": shared,
                    "context": context_text,
                    "from_start": t_rule.start,
                    "from_end": t_rule.end,
                }
            )

        target_rule_keys = {(r.context, s) for r in target_parse.rules for s in r.selectors}
        target_at_rules = {a.context: a for a in target_parse.at_rules}

        inserted_records: List[dict] = []
        insertion_ops: List[Tuple[int, str]] = []
        inserted_keys: Set[Tuple[Tuple[str, ...], str]] = set()

        if allow_insertions:
            for key, src_rule in panel_rule_by_key.items():
                context, selector = key
                if selector not in sync_set:
                    continue
                if key in target_rule_keys:
                    continue
                if selector in deny_selectors:
                    continue
                context_text = format_context(context)
                if context_text in deny_contexts:
                    continue
                if any(sel not in sync_set for sel in src_rule.selectors):
                    continue
                if key in inserted_keys:
                    continue

                if context:
                    at_block = target_at_rules.get(context)
                    if not at_block:
                        skipped_records.append(
                            {
                                "reason": "missing-target-context-for-insert",
                                "selector": selector,
                                "context": context_text,
                            }
                        )
                        continue
                    insert_pos = at_block.end - 1
                    insert_text = "\n" + src_rule.text + "\n"
                else:
                    insert_pos = len(target_text)
                    prefix = "\n" if not target_text.endswith("\n") else ""
                    insert_text = prefix + "\n" + src_rule.text + "\n"

                insertion_ops.append((insert_pos, insert_text))
                inserted_keys.add(key)
                inserted_records.append(
                    {
                        "selector": selector,
                        "context": context_text,
                        "insert_pos": insert_pos,
                    }
                )

        new_target_text = apply_ops(target_text, rule_replacements, insertion_ops)
        changed = new_target_text != target_text

        if args.mode == "apply" and changed:
            target_path.write_text(new_target_text, encoding="utf-8")

        report["targets"][target] = {
            "path": str(target_path),
            "sync_selector_count": len(sync_selectors),
            "sync_selectors": sync_selectors,
            "replacements_count": len(replacement_records),
            "insertions_count": len(inserted_records),
            "skipped_count": len(skipped_records),
            "changed": changed,
            "allow_insertions": allow_insertions,
            "replacements": replacement_records,
            "insertions": inserted_records,
            "skipped": skipped_records,
        }

    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport written to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
