#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "source ./activate-codex-home.sh" >&2
    exit 1
fi

_codex_utils_root="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CODEX_HOME="${CODEX_HOME:-$_codex_utils_root/.codex}"

case ":$PATH:" in
    *":$CODEX_HOME/bin:"*) ;;
    *) export PATH="$CODEX_HOME/bin:$PATH" ;;
esac

_downloads_root="$(cd -- "$_codex_utils_root/.." && pwd)"
_downloads_root="$(cd -- "$_downloads_root/.." && pwd)"
_shared_lambdas_node_modules="$_codex_utils_root/Downloads/lambdas/node_modules"

if [[ -d "$_downloads_root/lambdas/codeliver_all/dm-codeliver-brain/.codex" ]]; then
    _codex_utils_realpath="$_downloads_root/lambdas/codeliver_all/dm-codeliver-brain/.codex"
    export CODEDELIVER_BRAIN_CODEX="$(cd -- "$_codex_utils_realpath" && pwd)"
fi

if [[ -d "$_downloads_root/projects/cloud-repos-panel-brain/.codex" ]]; then
    _crp_brain="$_downloads_root/projects/cloud-repos-panel-brain/.codex"
    export CRP_BRAIN_CODEX="$(cd -- "$_crp_brain" && pwd)"
fi

if [[ -d "$_shared_lambdas_node_modules" ]]; then
    export CODEX_UTILITIES_LAMBDAS_NODE_MODULES="$_shared_lambdas_node_modules"
    case ":${NODE_PATH:-}:" in
        *":$CODEX_UTILITIES_LAMBDAS_NODE_MODULES:"*) ;;
        *) export NODE_PATH="$CODEX_UTILITIES_LAMBDAS_NODE_MODULES${NODE_PATH:+:$NODE_PATH}" ;;
    esac
fi

unset _codex_utils_root _downloads_root _codex_utils_realpath _crp_brain _shared_lambdas_node_modules
