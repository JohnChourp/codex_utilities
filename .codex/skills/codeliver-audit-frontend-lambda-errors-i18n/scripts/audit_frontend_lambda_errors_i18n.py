#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REF_FILE_RE = re.compile(r"^codeliver-(app|pos|panel|sap)-lambdas\.md$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
IGNORED_SECTIONS = {
    "API Ids -> API Names",
    "Πηγές",
    "Sources",
}

CUSTOM_ERROR_PATTERNS = [
    re.compile(r'new\s+CustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'CustomError\s*\([^)]*\|\|\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'throwCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'makeKnownError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'checkCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
]

PRESENT_POST_FAILURE_RE = re.compile(r'presentPostFailureAlert\s*\((?s:.*?)["\']([a-z0-9-]+)["\']')
LAMBDA_RESPONSES_KEY_RE = re.compile(r"lambdas_responses\.([a-z0-9-]+)\.")
CONSTANT_LAMBDA_RE = re.compile(
    r'(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:process\.env\.[A-Za-z_][A-Za-z0-9_]*\s*\|\|\s*)?["\']([a-z0-9-]+)["\']'
)
CALL_INVOKE_RE = re.compile(r"\b(?:lambda_invoke|lambdaInvoke|invokeLambda)\s*\(\s*([^\s,)\n]+)")
FUNCTION_NAME_RE = re.compile(r"FunctionName\s*:\s*([^\s,}\n]+)")
STRING_LITERAL_RE = re.compile(r'^["\']([a-z0-9-]+)["\']$')
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TODO_PLACEHOLDER_RE = re.compile(r"^\s*TODO\([^)]+\)\s*$", re.IGNORECASE)
GREEK_CHAR_RE = re.compile(r"[Α-Ωα-ω]")
SUPPORTED_LOCALE_FILES = {"el.json", "en.json"}


def first_existing_path(candidates, fallback: Path):
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return fallback


def default_refs_dir():
    home = Path.home()
    return first_existing_path(
        [
            home / ".codex" / "refs",
            Path("/Users/john/.codex/refs"),
            Path("/home/dm-soft-1/.codex/refs"),
        ],
        home / ".codex" / "refs",
    )


def default_projects_root():
    home = Path.home()
    return first_existing_path(
        [
            home / "Downloads" / "projects",
            Path("/Users/john/Downloads/projects"),
            Path("/home/dm-soft-1/Downloads/projects"),
        ],
        home / "Downloads" / "projects",
    )


def default_lambdas_root():
    home = Path.home()
    return first_existing_path(
        [
            home / "Downloads" / "lambdas",
            Path("/Users/john/Downloads/lambdas"),
            Path("/home/dm-soft-1/Downloads/lambdas"),
        ],
        home / "Downloads" / "lambdas",
    )


def default_tmp_dir():
    home = Path.home()
    return first_existing_path(
        [
            home / ".codex" / "tmp",
            Path("/Users/john/.codex/tmp"),
            Path("/home/dm-soft-1/.codex/tmp"),
        ],
        home / ".codex" / "tmp",
    )

ERROR_CODE_TRANSLATIONS = {
    "all_delivery_guys_rejected": {
        "en": "All delivery drivers rejected the request.",
        "el": "Όλοι οι διανομείς απέρριψαν το αίτημα.",
    },
    "already_active_route": {
        "en": "This route is already active.",
        "el": "Αυτή η διαδρομή είναι ήδη ενεργή.",
    },
    "db_error": {
        "en": "Database error.",
        "el": "Σφάλμα βάσης δεδομένων.",
    },
    "db_failed_create_request_calculation": {
        "en": "Failed to create request calculation in the database.",
        "el": "Αποτυχία δημιουργίας υπολογισμού αιτήματος στη βάση δεδομένων.",
    },
    "db_failed_querying_devices_sockets": {
        "en": "Failed to query device sockets from the database.",
        "el": "Αποτυχία ανάκτησης sockets συσκευών από τη βάση δεδομένων.",
    },
    "db_failed_to_create_route_path_calculation": {
        "en": "Failed to create route path calculation in the database.",
        "el": "Αποτυχία δημιουργίας υπολογισμού διαδρομής στη βάση δεδομένων.",
    },
    "db_failed_to_delete_route": {
        "en": "Failed to delete route from the database.",
        "el": "Αποτυχία διαγραφής διαδρομής από τη βάση δεδομένων.",
    },
    "db_failed_to_get_delivery_guy": {
        "en": "Failed to fetch delivery driver from the database.",
        "el": "Αποτυχία ανάκτησης διανομέα από τη βάση δεδομένων.",
    },
    "db_failed_to_get_delivery_guy_coordinates": {
        "en": "Failed to fetch delivery driver coordinates from the database.",
        "el": "Αποτυχία ανάκτησης συντεταγμένων διανομέα από τη βάση δεδομένων.",
    },
    "db_failed_to_get_delivery_guys": {
        "en": "Failed to fetch delivery drivers from the database.",
        "el": "Αποτυχία ανάκτησης διανομέων από τη βάση δεδομένων.",
    },
    "db_failed_to_get_group": {
        "en": "Failed to fetch group from the database.",
        "el": "Αποτυχία ανάκτησης group από τη βάση δεδομένων.",
    },
    "db_failed_to_get_panel_user": {
        "en": "Failed to fetch panel user from the database.",
        "el": "Αποτυχία ανάκτησης χρήστη panel από τη βάση δεδομένων.",
    },
    "db_failed_to_get_request": {
        "en": "Failed to fetch request from the database.",
        "el": "Αποτυχία ανάκτησης αιτήματος από τη βάση δεδομένων.",
    },
    "db_failed_to_get_requests": {
        "en": "Failed to fetch requests from the database.",
        "el": "Αποτυχία ανάκτησης αιτημάτων από τη βάση δεδομένων.",
    },
    "db_failed_to_get_route": {
        "en": "Failed to fetch route from the database.",
        "el": "Αποτυχία ανάκτησης διαδρομής από τη βάση δεδομένων.",
    },
    "db_failed_to_get_route_path": {
        "en": "Failed to get route path from the database.",
        "el": "Αποτυχία λήψης route path από τη βάση δεδομένων.",
    },
    "db_failed_to_get_route_paths": {
        "en": "Failed to fetch route paths from the database.",
        "el": "Αποτυχία ανάκτησης route paths από τη βάση δεδομένων.",
    },
    "db_failed_to_get_user": {
        "en": "Failed to fetch user from the database.",
        "el": "Αποτυχία ανάκτησης χρήστη από τη βάση δεδομένων.",
    },
    "db_failed_to_query_delivery_guys": {
        "en": "Failed to query delivery drivers from the database.",
        "el": "Αποτυχία αναζήτησης διανομέων στη βάση δεδομένων.",
    },
    "db_failed_to_query_delivery_guys_actions": {
        "en": "Failed to query delivery driver actions from the database.",
        "el": "Αποτυχία αναζήτησης ενεργειών διανομέων στη βάση δεδομένων.",
    },
    "db_failed_to_query_group_zones": {
        "en": "Failed to query group zones from the database.",
        "el": "Αποτυχία αναζήτησης ζωνών group στη βάση δεδομένων.",
    },
    "db_failed_to_query_request_calculations": {
        "en": "Failed to query request calculations from the database.",
        "el": "Αποτυχία αναζήτησης υπολογισμών αιτημάτων στη βάση δεδομένων.",
    },
    "db_failed_to_query_requests": {
        "en": "Failed to query requests from the database.",
        "el": "Αποτυχία αναζήτησης αιτημάτων στη βάση δεδομένων.",
    },
    "db_failed_to_query_requests_actions": {
        "en": "Failed to query request actions from the database.",
        "el": "Αποτυχία αναζήτησης ενεργειών αιτημάτων στη βάση δεδομένων.",
    },
    "db_failed_to_query_route_paths": {
        "en": "Failed to query route paths from the database.",
        "el": "Αποτυχία αναζήτησης route paths στη βάση δεδομένων.",
    },
    "db_failed_to_query_routes": {
        "en": "Failed to query routes from the database.",
        "el": "Αποτυχία αναζήτησης διαδρομών στη βάση δεδομένων.",
    },
    "db_failed_to_query_routes_paths_calculations": {
        "en": "Failed to query route path calculations from the database.",
        "el": "Αποτυχία αναζήτησης υπολογισμών διαδρομών στη βάση δεδομένων.",
    },
    "db_failed_to_update_delivery_guy": {
        "en": "Failed to update delivery driver in the database.",
        "el": "Αποτυχία ενημέρωσης διανομέα στη βάση δεδομένων.",
    },
    "db_failed_to_update_delivery_guy_current_route_id": {
        "en": "Failed to update delivery driver current route in the database.",
        "el": "Αποτυχία ενημέρωσης της τρέχουσας διαδρομής διανομέα στη βάση δεδομένων.",
    },
    "db_failed_to_update_route_status_canceled": {
        "en": "Failed to set route status to canceled in the database.",
        "el": "Αποτυχία ενημέρωσης κατάστασης διαδρομής σε ακυρωμένη στη βάση δεδομένων.",
    },
    "db_failed_to_update_route_status_merged_and_delivery_guy_status_to_accepted": {
        "en": "Failed to update merged route and delivery driver accepted status.",
        "el": "Αποτυχία ενημέρωσης συγχωνευμένης διαδρομής και κατάστασης αποδοχής διανομέα.",
    },
    "db_query_failed_to_query_delivery_guys_coordinates": {
        "en": "Failed to query delivery driver coordinates from the database.",
        "el": "Αποτυχία αναζήτησης συντεταγμένων διανομέων στη βάση δεδομένων.",
    },
    "delivery_guy_not_in_route": {
        "en": "Delivery driver is not part of this route.",
        "el": "Ο διανομέας δεν ανήκει σε αυτή τη διαδρομή.",
    },
    "dynamo_db_error": {
        "en": "DynamoDB error.",
        "el": "Σφάλμα DynamoDB.",
    },
    "dynamo_error": {
        "en": "DynamoDB error.",
        "el": "Σφάλμα DynamoDB.",
    },
    "failed_to_complete_return_to_base": {
        "en": "Failed to complete return to base.",
        "el": "Αποτυχία ολοκλήρωσης επιστροφής στη βάση.",
    },
    "get_current_route_error": {
        "en": "Failed to fetch current route.",
        "el": "Αποτυχία ανάκτησης τρέχουσας διαδρομής.",
    },
    "get_route_to_accept_error": {
        "en": "Failed to fetch route to accept.",
        "el": "Αποτυχία ανάκτησης διαδρομής προς αποδοχή.",
    },
    "group_does_not_exists": {
        "en": "Group does not exist.",
        "el": "Το group δεν υπάρχει.",
    },
    "invalid_body": {
        "en": "Invalid request body.",
        "el": "Μη έγκυρο σώμα αιτήματος.",
    },
    "invalid_group_or_delivery_guy": {
        "en": "Invalid group or delivery driver.",
        "el": "Μη έγκυρο group ή διανομέας.",
    },
    "invalid_params": {
        "en": "Invalid parameters.",
        "el": "Μη έγκυρες παράμετροι.",
    },
    "invalid_remove_request_payload": {
        "en": "Invalid remove-request payload.",
        "el": "Μη έγκυρο payload αφαίρεσης αιτήματος.",
    },
    "invalid_reorder_payload": {
        "en": "Invalid reorder payload.",
        "el": "Μη έγκυρο payload αναδιάταξης.",
    },
    "invoke_codeliver_routes_merge_error": {
        "en": "Failed to invoke codeliver-routes-merge.",
        "el": "Αποτυχία κλήσης του codeliver-routes-merge.",
    },
    "lambda_invoke_codeliver_routes_merge_error": {
        "en": "Lambda invoke failed for codeliver-routes-merge.",
        "el": "Αποτυχία invoke lambda για το codeliver-routes-merge.",
    },
    "missing_active_route": {
        "en": "Active route is missing.",
        "el": "Λείπει ενεργή διαδρομή.",
    },
    "missing_customer_leg_for_merge": {
        "en": "Missing customer leg required for merge.",
        "el": "Λείπει το customer leg που απαιτείται για συγχώνευση.",
    },
    "missing_date_from": {
        "en": "Missing date_from parameter.",
        "el": "Λείπει η παράμετρος date_from.",
    },
    "missing_delivery_guy_id": {
        "en": "Missing delivery_guy_id parameter.",
        "el": "Λείπει η παράμετρος delivery_guy_id.",
    },
    "missing_request_paths_to_merge": {
        "en": "Missing request paths required for merge.",
        "el": "Λείπουν route paths αιτημάτων που απαιτούνται για συγχώνευση.",
    },
    "missing_route_id": {
        "en": "Missing route_id parameter.",
        "el": "Λείπει η παράμετρος route_id.",
    },
    "missing_store_leg_for_merge": {
        "en": "Missing store leg required for merge.",
        "el": "Λείπει το store leg που απαιτείται για συγχώνευση.",
    },
    "not_found_delviery_guy": {
        "en": "Delivery driver was not found.",
        "el": "Ο διανομέας δεν βρέθηκε.",
    },
    "not_found_either_new_requests_or_route_or_route_paths_or_delivery_guy_to_merge": {
        "en": "Missing required data (new requests, route, route paths, or delivery driver) for merge.",
        "el": "Δεν βρέθηκαν απαιτούμενα δεδομένα (νέα αιτήματα, διαδρομή, route paths ή διανομέας) για συγχώνευση.",
    },
    "not_found_either_route_paths_or_requests_that_exist_or_requests_or_route_or_route_paths_or_delivery_guy_or_current_route_id_to_merge": {
        "en": "Missing required route/request data needed for merge.",
        "el": "Δεν βρέθηκαν απαιτούμενα δεδομένα διαδρομής/αιτημάτων για συγχώνευση.",
    },
    "not_found_route_or_requests_after_removal": {
        "en": "Route or requests were not found after removal.",
        "el": "Δεν βρέθηκε διαδρομή ή αιτήματα μετά την αφαίρεση.",
    },
    "not_found_route_or_requests_to_reorder": {
        "en": "Route or requests to reorder were not found.",
        "el": "Δεν βρέθηκε διαδρομή ή αιτήματα για αναδιάταξη.",
    },
    "request_not_found": {
        "en": "Request was not found.",
        "el": "Το αίτημα δεν βρέθηκε.",
    },
    "request_not_found_in_route": {
        "en": "Request was not found in route.",
        "el": "Το αίτημα δεν βρέθηκε στη διαδρομή.",
    },
    "return_to_base_completion_timeout": {
        "en": "Return-to-base completion timed out before the route path became ready.",
        "el": "Η ολοκλήρωση επιστροφής στη βάση έληξε πριν γίνει έτοιμη η διαδρομή.",
    },
    "route_not_found": {
        "en": "Route was not found.",
        "el": "Η διαδρομή δεν βρέθηκε.",
    },
    "route_paths_calculations_error": {
        "en": "Route path calculations failed.",
        "el": "Αποτυχία υπολογισμών route paths.",
    },
    "someone_else_accepted": {
        "en": "This route was accepted by another user.",
        "el": "Η διαδρομή έγινε αποδεκτή από άλλον χρήστη.",
    },
    "total_paths_sum_after_merge_bigger_than_group_max_requests_in_route": {
        "en": "Merged route exceeds group maximum requests per route.",
        "el": "Η συγχωνευμένη διαδρομή ξεπερνά το μέγιστο αιτημάτων ανά διαδρομή του group.",
    },
    "unauthorized_access": {
        "en": "Unauthorized access.",
        "el": "Μη εξουσιοδοτημένη πρόσβαση.",
    },
    "update_delivery_guy_error": {
        "en": "Failed to update delivery driver.",
        "el": "Αποτυχία ενημέρωσης διανομέα.",
    },
    "update_requests_error": {
        "en": "Failed to update requests.",
        "el": "Αποτυχία ενημέρωσης αιτημάτων.",
    },
    "update_route_to_accept_error": {
        "en": "Failed to update route for acceptance.",
        "el": "Αποτυχία ενημέρωσης διαδρομής προς αποδοχή.",
    },
    "user_does_not_exist": {
        "en": "User does not exist.",
        "el": "Ο χρήστης δεν υπάρχει.",
    },
}


def parse_ref_file(path: Path):
    project = path.name.replace("-lambdas.md", "")
    lambdas = []
    seen = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = SECTION_RE.match(line.strip())
        if not match:
            continue
        section = match.group(1).strip()
        if section in IGNORED_SECTIONS:
            continue
        if section.startswith("Observed ") or section.startswith("Σκοπός:"):
            continue
        if section not in seen:
            seen.add(section)
            lambdas.append(section)
    return project, lambdas


def load_frontend_refs(refs_dir: Path):
    project_to_lambdas = {}
    for ref_file in sorted(refs_dir.glob("codeliver-*-lambdas.md")):
        if not REF_FILE_RE.match(ref_file.name):
            continue
        project, lambdas = parse_ref_file(ref_file)
        project_to_lambdas[project] = lambdas
    return project_to_lambdas


def build_lambda_index(lambdas_root: Path):
    index = defaultdict(list)
    for group_dir in sorted(lambdas_root.iterdir()):
        if not group_dir.is_dir():
            continue
        if group_dir.name in {"node_modules", ".git"}:
            continue
        for lambda_dir in sorted(group_dir.iterdir()):
            if lambda_dir.is_dir():
                index[lambda_dir.name].append(str(lambda_dir.resolve()))
    return index


def iter_lambda_code_files(lambda_dir: Path):
    for path in lambda_dir.rglob("*.js"):
        parts = set(path.parts)
        if "node_modules" in parts or "__tests__" in parts or "test" in parts:
            continue
        if path.name.endswith(".test.js"):
            continue
        yield path


def extract_error_codes_from_text(text: str):
    codes = set()
    for pattern in CUSTOM_ERROR_PATTERNS:
        for match in pattern.finditer(text):
            code = match.group(1).strip()
            if code:
                codes.add(code)
    return codes


def extract_response_fields_from_text(text: str):
    fields = set()
    if re.search(r"\bcomment_id\s*:", text):
        fields.add("comment_id")
    if re.search(r"\bcomments\s*:", text):
        fields.add("comments")
    return fields


def resolve_invoked_token(token: str, constants_map: dict):
    token = token.strip()
    string_match = STRING_LITERAL_RE.match(token)
    if string_match:
        return string_match.group(1)
    if IDENTIFIER_RE.match(token):
        return constants_map.get(token)
    return None


def extract_downstream_lambda_names(text: str):
    constants_map = {}
    for match in CONSTANT_LAMBDA_RE.finditer(text):
        constants_map[match.group(1)] = match.group(2)

    names = set()
    for match in CALL_INVOKE_RE.finditer(text):
        name = resolve_invoked_token(match.group(1), constants_map)
        if name:
            names.add(name)

    for match in FUNCTION_NAME_RE.finditer(text):
        name = resolve_invoked_token(match.group(1), constants_map)
        if name:
            names.add(name)

    return {name for name in names if "-" in name}


def detect_project_nested_lambdas(project_root: Path):
    nested_lambdas = set()
    app_root = project_root / "src" / "app"
    if not app_root.exists():
        return nested_lambdas

    for ts_file in app_root.rglob("*.ts"):
        text = ts_file.read_text(encoding="utf-8", errors="ignore")
        for match in PRESENT_POST_FAILURE_RE.finditer(text):
            nested_lambdas.add(match.group(1))
        for match in LAMBDA_RESPONSES_KEY_RE.finditer(text):
            nested_lambdas.add(match.group(1))
    return nested_lambdas


def load_i18n_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_i18n_file(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_placeholder_translation(value: str):
    return bool(TODO_PLACEHOLDER_RE.match(value.strip()))


def locale_language_code_from_file_name(file_name: str):
    locale = Path(file_name).stem.lower()
    if locale in {"el", "gr", "greek"}:
        return "el"
    return "en"


def is_unusable_translation(value: str, target_locale_file: str):
    stripped = value.strip()
    if is_placeholder_translation(stripped):
        return True
    locale_code = locale_language_code_from_file_name(target_locale_file)
    if locale_code == "en" and GREEK_CHAR_RE.search(stripped):
        return True
    return False


def generate_translation_from_error_code(error_code: str, target_locale_file: str):
    locale_code = locale_language_code_from_file_name(target_locale_file)
    exact = ERROR_CODE_TRANSLATIONS.get(error_code, {})
    if locale_code in exact:
        return exact[locale_code]
    if "en" in exact:
        return exact["en"]
    text = re.sub(r"[_\-.]+", " ", error_code).strip()
    if locale_code == "el":
        return f"Σφάλμα: {text}."
    return f"{text.capitalize()}."


def check_translation_exists(
    i18n_data: dict,
    translation_kind: str,
    entry_lambda: str,
    error_code: str,
    target_locale_file: str,
):
    return (
        get_translation_value(
            i18n_data, translation_kind, entry_lambda, error_code, target_locale_file
        )
        is not None
    )


def get_translation_value(
    i18n_data: dict,
    translation_kind: str,
    entry_lambda: str,
    error_code: str,
    target_locale_file: str,
):
    if translation_kind == "root":
        value = i18n_data.get(error_code)
        if not isinstance(value, str) or not value.strip():
            return None
        return None if is_unusable_translation(value, target_locale_file) else value

    lambdas_responses = i18n_data.get("lambdas_responses")
    if not isinstance(lambdas_responses, dict):
        return None
    lambda_map = lambdas_responses.get(entry_lambda)
    if not isinstance(lambda_map, dict):
        return None
    value = lambda_map.get(error_code)
    if not isinstance(value, str) or not value.strip():
        return None
    return None if is_unusable_translation(value, target_locale_file) else value


def select_fallback_translation(
    i18n_cache: dict,
    current_i18n_key: str,
    translation_kind: str,
    entry_lambda: str,
    error_code: str,
    target_locale_file: str,
):
    target_locale_code = locale_language_code_from_file_name(target_locale_file)
    for i18n_key, i18n_data in i18n_cache.items():
        if i18n_key == current_i18n_key:
            continue
        candidate_file_name = Path(i18n_key).name
        if locale_language_code_from_file_name(candidate_file_name) != target_locale_code:
            continue
        value = get_translation_value(
            i18n_data,
            translation_kind,
            entry_lambda,
            error_code,
            candidate_file_name,
        )
        if value:
            return value, "copied_from_other_locale"
    return (
        generate_translation_from_error_code(error_code, target_locale_file),
        "generated_from_error_code",
    )


def ensure_translation(
    i18n_data: dict,
    translation_kind: str,
    entry_lambda: str,
    error_code: str,
    placeholder: str,
    target_locale_file: str,
    apply_changes: bool = True,
):
    if translation_kind == "root":
        existing_value = i18n_data.get(error_code)
        if (
            isinstance(existing_value, str)
            and existing_value.strip()
            and not is_unusable_translation(existing_value, target_locale_file)
        ):
            return False, None
        if apply_changes:
            i18n_data[error_code] = placeholder
        return True, None

    lambdas_responses = i18n_data.get("lambdas_responses")
    if lambdas_responses is None:
        if apply_changes:
            i18n_data["lambdas_responses"] = {}
            lambdas_responses = i18n_data["lambdas_responses"]
        else:
            lambdas_responses = {}

    if not isinstance(lambdas_responses, dict):
        return False, "invalid_lambdas_responses_container"

    lambda_map = lambdas_responses.get(entry_lambda)
    if lambda_map is None:
        if apply_changes:
            lambdas_responses[entry_lambda] = {}
            lambda_map = lambdas_responses[entry_lambda]
        else:
            lambda_map = {}

    if not isinstance(lambda_map, dict):
        return False, "invalid_lambda_translation_container"

    existing_value = lambda_map.get(error_code)
    if (
        isinstance(existing_value, str)
        and existing_value.strip()
        and not is_unusable_translation(existing_value, target_locale_file)
    ):
        return False, None

    if apply_changes:
        lambda_map[error_code] = placeholder
    return True, None


def md_escape(value):
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def write_markdown_report(path: Path, report: dict):
    rows = report["rows"]
    unresolved = report["unresolved"]
    summary = report["summary"]

    lines = [
        "# Frontend Lambda Error Translation Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Mode: `{report['mode']}`",
        f"- Languages: `{report['languages']}`",
        f"- Depth: `{report['depth']}`",
        "",
        "## Summary",
        f"- Total rows: `{summary['total_rows']}`",
        f"- found: `{summary['found']}`",
        f"- created: `{summary['created']}`",
        f"- missing: `{summary['missing']}`",
        f"- skipped: `{summary['skipped']}`",
        f"- unresolved mappings: `{summary['unresolved_mappings']}`",
        "",
    ]

    if unresolved:
        lines.append("## Unresolved mappings")
        for item in unresolved:
            lines.append(
                f"- `{item['frontend_project']}` -> `{item['lambda_name']}` ({item['kind']})"
            )
        lines.append("")

    non_found_rows = [row for row in rows if row["status"] != "found"]
    lines.append("## Non-found rows")
    if not non_found_rows:
        lines.append("- None")
        lines.append("")
    else:
        lines.extend(
            [
                "",
                "| frontend_project | entry_lambda | downstream_lambda | error_code | field | translation_path | status | language_file | reason |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in non_found_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(row.get("frontend_project", "")),
                        md_escape(row.get("entry_lambda", "")),
                        md_escape(row.get("downstream_lambda", "")),
                        md_escape(row.get("error_code", "")),
                        md_escape(row.get("field", "")),
                        md_escape(row.get("translation_path", "")),
                        md_escape(row.get("status", "")),
                        md_escape(row.get("language_file", "")),
                        md_escape(row.get("reason", "")),
                    ]
                )
                + " |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_languages_spec(languages: str):
    if languages.strip().lower() == "all":
        return set(SUPPORTED_LOCALE_FILES)
    values = [item.strip() for item in languages.split(",") if item.strip()]
    selected = {f"{value}.json" if not value.endswith(".json") else value for value in values}
    unsupported = sorted(selected - SUPPORTED_LOCALE_FILES)
    if unsupported:
        raise SystemExit(f"unsupported locales requested: {unsupported}. Only el,en are allowed.")
    return selected


def analyze_lambda_folder(lambda_dir: Path):
    all_texts = []
    response_fields = set()
    error_codes = set()
    downstream_names = set()

    for js_file in iter_lambda_code_files(lambda_dir):
        text = js_file.read_text(encoding="utf-8", errors="ignore")
        all_texts.append(text)
        response_fields |= extract_response_fields_from_text(text)
        error_codes |= extract_error_codes_from_text(text)
        downstream_names |= extract_downstream_lambda_names(text)

    return {
        "response_fields": response_fields,
        "error_codes": error_codes,
        "downstream_names": downstream_names,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Audit/autofix frontend-visible lambda error translation coverage."
    )
    parser.add_argument("--mode", choices=["audit", "autofix"], default="autofix")
    parser.add_argument("--languages", default="el,en", help="comma-separated list, supported only: el,en")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--projects-root", default=str(default_projects_root()))
    parser.add_argument("--lambdas-root", default=str(default_lambdas_root()))
    parser.add_argument("--refs-dir", default=str(default_refs_dir()))
    parser.add_argument(
        "--report-json",
        default=str(default_tmp_dir() / "frontend-lambda-errors-i18n-report.json"),
    )
    parser.add_argument(
        "--report-md",
        default=str(default_tmp_dir() / "frontend-lambda-errors-i18n-report.md"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.depth != 1:
        raise SystemExit("Only --depth 1 is supported by policy.")

    projects_root = Path(args.projects_root)
    lambdas_root = Path(args.lambdas_root)
    refs_dir = Path(args.refs_dir)
    report_json_path = Path(args.report_json)
    report_md_path = Path(args.report_md)
    selected_languages = parse_languages_spec(args.languages)

    if not projects_root.exists():
        raise SystemExit(f"projects root not found: {projects_root}")
    if not lambdas_root.exists():
        raise SystemExit(f"lambdas root not found: {lambdas_root}")
    if not refs_dir.exists():
        raise SystemExit(f"refs dir not found: {refs_dir}")

    project_to_entry_lambdas = load_frontend_refs(refs_dir)
    lambda_index = build_lambda_index(lambdas_root)

    unresolved = []
    rows = []
    changed_i18n_files = set()
    i18n_cache = {}
    lambda_analysis_cache = {}

    for frontend_project, entry_lambdas in sorted(project_to_entry_lambdas.items()):
        project_root = projects_root / "codeliver" / frontend_project
        i18n_dir = project_root / "src" / "assets" / "i18n"
        if not i18n_dir.exists():
            unresolved.append(
                {
                    "frontend_project": frontend_project,
                    "lambda_name": "",
                    "kind": "missing_i18n_dir",
                }
            )
            continue

        i18n_files = sorted(i18n_dir.glob("*.json"))
        if selected_languages is not None:
            i18n_files = [path for path in i18n_files if path.name in selected_languages]

        if not i18n_files:
            unresolved.append(
                {
                    "frontend_project": frontend_project,
                    "lambda_name": "",
                    "kind": "no_matching_i18n_files",
                }
            )
            continue

        nested_lambdas = detect_project_nested_lambdas(project_root)

        for entry_lambda in entry_lambdas:
            matches = lambda_index.get(entry_lambda, [])
            if len(matches) != 1:
                kind = "entry_unresolved" if len(matches) == 0 else "entry_ambiguous"
                unresolved.append(
                    {
                        "frontend_project": frontend_project,
                        "lambda_name": entry_lambda,
                        "kind": kind,
                    }
                )
                rows.append(
                    {
                        "frontend_project": frontend_project,
                        "entry_lambda": entry_lambda,
                        "resolved_lambda_path": None,
                        "downstream_lambda": "",
                        "error_code": "",
                        "field": "",
                        "translation_path": "",
                        "status": "skipped",
                        "language_file": "",
                        "reason": kind,
                    }
                )
                continue

            entry_path = Path(matches[0])
            if str(entry_path) not in lambda_analysis_cache:
                lambda_analysis_cache[str(entry_path)] = analyze_lambda_folder(entry_path)
            entry_analysis = lambda_analysis_cache[str(entry_path)]

            entry_fields = entry_analysis["response_fields"] or {"comment_id"}
            entry_error_codes = set(entry_analysis["error_codes"])
            downstream_names = set(entry_analysis["downstream_names"])
            downstream_codes = set()

            for downstream_name in sorted(downstream_names):
                downstream_matches = lambda_index.get(downstream_name, [])
                if len(downstream_matches) != 1:
                    kind = (
                        "downstream_unresolved"
                        if len(downstream_matches) == 0
                        else "downstream_ambiguous"
                    )
                    unresolved.append(
                        {
                            "frontend_project": frontend_project,
                            "lambda_name": downstream_name,
                            "kind": kind,
                        }
                    )
                    continue

                downstream_path = Path(downstream_matches[0])
                if str(downstream_path) not in lambda_analysis_cache:
                    lambda_analysis_cache[str(downstream_path)] = analyze_lambda_folder(
                        downstream_path
                    )
                downstream_analysis = lambda_analysis_cache[str(downstream_path)]
                downstream_codes |= set(downstream_analysis["error_codes"])

            all_error_codes = sorted(entry_error_codes | downstream_codes)
            if not all_error_codes:
                rows.append(
                    {
                        "frontend_project": frontend_project,
                        "entry_lambda": entry_lambda,
                        "resolved_lambda_path": str(entry_path),
                        "downstream_lambda": "",
                        "error_code": "",
                        "field": ",".join(sorted(entry_fields)),
                        "translation_path": "root"
                        if entry_lambda not in nested_lambdas
                        else f"lambdas_responses.{entry_lambda}",
                        "status": "skipped",
                        "language_file": "",
                        "reason": "no_custom_error_codes_detected",
                    }
                )
                continue

            translation_kind = "nested" if entry_lambda in nested_lambdas else "root"
            translation_path = (
                f"lambdas_responses.{entry_lambda}"
                if translation_kind == "nested"
                else "root"
            )

            for preload_i18n_file in i18n_files:
                preload_key = str(preload_i18n_file.resolve())
                if preload_key not in i18n_cache:
                    i18n_cache[preload_key] = load_i18n_file(preload_i18n_file)

            for i18n_file in i18n_files:
                i18n_key = str(i18n_file.resolve())
                if i18n_key not in i18n_cache:
                    i18n_cache[i18n_key] = load_i18n_file(i18n_file)
                i18n_data = i18n_cache[i18n_key]

                for error_code in all_error_codes:
                    exists = check_translation_exists(
                        i18n_data=i18n_data,
                        translation_kind=translation_kind,
                        entry_lambda=entry_lambda,
                        error_code=error_code,
                        target_locale_file=i18n_file.name,
                    )

                    status = "found" if exists else "missing"
                    reason = ""

                    if not exists and args.mode == "autofix":
                        fallback_text, fallback_source = select_fallback_translation(
                            i18n_cache=i18n_cache,
                            current_i18n_key=i18n_key,
                            translation_kind=translation_kind,
                            entry_lambda=entry_lambda,
                            error_code=error_code,
                            target_locale_file=i18n_file.name,
                        )
                        created, collision_reason = ensure_translation(
                            i18n_data=i18n_data,
                            translation_kind=translation_kind,
                            entry_lambda=entry_lambda,
                            error_code=error_code,
                            placeholder=fallback_text,
                            target_locale_file=i18n_file.name,
                            apply_changes=not args.dry_run,
                        )
                        if collision_reason:
                            status = "skipped"
                            reason = collision_reason
                        elif created:
                            if args.dry_run:
                                status = "missing"
                                reason = "dry_run"
                            else:
                                status = "created"
                                reason = fallback_source
                                changed_i18n_files.add(i18n_key)

                    downstream_lambda = ""
                    if error_code in downstream_codes and error_code not in entry_error_codes:
                        downstream_lambda = "one-hop-downstream"

                    for field in sorted(entry_fields):
                        rows.append(
                            {
                                "frontend_project": frontend_project,
                                "entry_lambda": entry_lambda,
                                "resolved_lambda_path": str(entry_path),
                                "downstream_lambda": downstream_lambda,
                                "error_code": error_code,
                                "field": field,
                                "translation_path": translation_path,
                                "status": status,
                                "language_file": i18n_key,
                                "reason": reason,
                            }
                        )

    if args.mode == "autofix" and not args.dry_run:
        for path_str in sorted(changed_i18n_files):
            save_i18n_file(Path(path_str), i18n_cache[path_str])

    status_counts = Counter(row["status"] for row in rows)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "languages": args.languages,
        "depth": args.depth,
        "projects_root": str(projects_root.resolve()),
        "lambdas_root": str(lambdas_root.resolve()),
        "refs_dir": str(refs_dir.resolve()),
        "rows": rows,
        "unresolved": unresolved,
        "summary": {
            "total_rows": len(rows),
            "found": status_counts.get("found", 0),
            "created": status_counts.get("created", 0),
            "missing": status_counts.get("missing", 0),
            "skipped": status_counts.get("skipped", 0),
            "unresolved_mappings": len(unresolved),
            "changed_i18n_files": len(changed_i18n_files),
        },
    }

    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown_report(report_md_path, report)

    print(
        "summary",
        json.dumps(
            {
                "report_json": str(report_json_path),
                "report_md": str(report_md_path),
                **report["summary"],
            },
            ensure_ascii=False,
        ),
    )


if __name__ == "__main__":
    main()
