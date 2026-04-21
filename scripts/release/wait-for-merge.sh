#!/usr/bin/env bash
# Poll a release PR until it reaches a terminal state, with exponential backoff.
#
# Arguments:
#   $1  Branch (head ref) of the PR to watch. Required.
#
# Environment overrides (all optional, seconds):
#   WAIT_FOR_MERGE_WARMUP     Initial sleep before first poll.                 default 60
#   WAIT_FOR_MERGE_MAX_TOTAL  Hard ceiling on total wall-clock wait.           default 900
#   WAIT_FOR_MERGE_BASE       Base backoff unit.                               default 20
#   WAIT_FOR_MERGE_CAP        Max sleep between polls after exponential ramp. default 120
#   WAIT_FOR_MERGE_GH         Override `gh` command (tests inject a fake).     default "gh"
#
# Exit codes:
#   0  PR reached MERGED state.
#   1  PR reached CLOSED (without merge), or total wait exceeded
#      WAIT_FOR_MERGE_MAX_TOTAL without a terminal state.
#
# Motivation: the prior inline 30×10s=300s poll timed out whenever
# Super-Linter (~5 min warm-up + ~5 min first-run-on-PR) on the release PR
# took longer than the window, leaving the release PR orphaned and
# requiring the self-heal pre-clean block on the NEXT scheduled run to
# recover. Warming up for 60s, then backing off exponentially up to a
# 15-min ceiling, covers typical Super-Linter runs without burning
# API-call budget at a fixed 10s cadence.

set -euo pipefail

BRANCH="${1:?usage: wait-for-merge.sh <BRANCH>}"

WARMUP="${WAIT_FOR_MERGE_WARMUP:-60}"
MAX_TOTAL="${WAIT_FOR_MERGE_MAX_TOTAL:-900}"
BASE="${WAIT_FOR_MERGE_BASE:-20}"
CAP="${WAIT_FOR_MERGE_CAP:-120}"
GH_CMD="${WAIT_FOR_MERGE_GH:-gh}"

poll_state() {
  "$GH_CMD" pr view "$BRANCH" --json state --jq '.state' 2>/dev/null
}

fail_with_diagnostics() {
  local reason="$1"
  echo "::error::${reason}" >&2
  # Best-effort diagnostic capture — don't let failure inside this
  # block mask the original exit status.
  "$GH_CMD" pr view "$BRANCH" \
    --json state,mergeStateStatus,mergeable,reviewDecision,statusCheckRollup \
    >&2 2>/dev/null || true
  return 1
}

elapsed=0

echo "Waiting ${WARMUP}s before first poll..."
sleep "$WARMUP"
elapsed=$((elapsed + WARMUP))

attempt=1
sleep_for="$BASE"

while [ "$elapsed" -lt "$MAX_TOTAL" ]; do
  state="$(poll_state || true)"
  case "$state" in
  MERGED)
    echo "PR merged successfully after ${elapsed}s"
    exit 0
    ;;
  CLOSED)
    fail_with_diagnostics "PR was closed without merging after ${elapsed}s"
    exit 1
    ;;
  OPEN | "")
    echo "Attempt ${attempt}: state=${state:-unknown}, elapsed=${elapsed}s, sleeping ${sleep_for}s"
    ;;
  *)
    echo "Attempt ${attempt}: unexpected state '${state}', sleeping ${sleep_for}s"
    ;;
  esac

  sleep "$sleep_for"
  elapsed=$((elapsed + sleep_for))
  attempt=$((attempt + 1))

  # Exponential ramp capped at $CAP.
  sleep_for=$((sleep_for * 2))
  if [ "$sleep_for" -gt "$CAP" ]; then
    sleep_for="$CAP"
  fi
done

fail_with_diagnostics "PR did not merge within ${MAX_TOTAL}s (${attempt} attempts)"
exit 1
