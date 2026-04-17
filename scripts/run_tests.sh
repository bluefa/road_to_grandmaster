#!/usr/bin/env bash
# Build and test a competitive programming solution against sample inputs.
#
# Usage:
#   ./scripts/run_tests.sh <problem-dir>
#   ./scripts/run_tests.sh problems/atc/atc-abc436_g
#
# Expects:
#   <problem-dir>/workspace/main.cpp
#   <problem-dir>/workspace/testcases/sample_input_N.txt
#   <problem-dir>/workspace/testcases/sample_output_N.txt  (optional per N)
#
# Produces:
#   <problem-dir>/workspace/.solution  (compiled binary, git-ignored)
#   <problem-dir>/workspace/summary.md (PASS/FAIL table)
#
# Exit codes:
#   0  all tests passed
#   1  build failed or any test failed
#   2  usage error (missing args, missing main.cpp, etc.)

set -u

# ---- colors ----
if [[ -t 1 ]]; then
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  RED=""; GREEN=""; YELLOW=""; BOLD=""; RESET=""
fi

# ---- args ----
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <problem-dir>" >&2
  exit 2
fi

PROBLEM_DIR="${1%/}"
# allow passing either problem dir or workspace dir directly
if [[ -f "$PROBLEM_DIR/main.cpp" && -d "$PROBLEM_DIR/testcases" ]]; then
  WORKSPACE="$PROBLEM_DIR"
else
  WORKSPACE="$PROBLEM_DIR/workspace"
fi

MAIN_CPP="$WORKSPACE/main.cpp"
TESTCASE_DIR="$WORKSPACE/testcases"
SUMMARY="$WORKSPACE/summary.md"
BINARY="$WORKSPACE/.solution"
TIMEOUT_SEC=5

# Portable timeout: GNU timeout (linux/brew coreutils) -> gtimeout (brew) -> perl fallback.
# GNU timeout exits 124 on timeout; perl's SIGALRM makes the child exit 142 (128+14).
# We treat both as TLE.
run_with_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  else
    perl -e 'alarm shift @ARGV; exec { $ARGV[0] } @ARGV' "$secs" "$@"
  fi
}

# ---- validate ----
if [[ ! -f "$MAIN_CPP" ]]; then
  echo "${RED}Error:${RESET} main.cpp not found at $MAIN_CPP" >&2
  exit 2
fi

mkdir -p "$TESTCASE_DIR"

# ---- build ----
BUILD_LOG=$(mktemp)
trap 'rm -f "$BUILD_LOG"' EXIT

if g++ -std=c++17 -O2 -Wall -o "$BINARY" "$MAIN_CPP" 2> "$BUILD_LOG"; then
  echo "${GREEN}[BUILD]${RESET} OK"
  BUILD_STATUS="PASS"
else
  echo "${RED}[BUILD]${RESET} FAIL"
  cat "$BUILD_LOG" >&2
  {
    echo "# Test Summary"
    echo ""
    echo "Build: FAIL"
    echo ""
    echo '```'
    cat "$BUILD_LOG"
    echo '```'
  } > "$SUMMARY"
  exit 1
fi

# ---- discover test cases ----
shopt -s nullglob
INPUTS=("$TESTCASE_DIR"/sample_input_*.txt)
shopt -u nullglob

if [[ ${#INPUTS[@]} -eq 0 ]]; then
  echo "${YELLOW}[WARN]${RESET} No test cases in $TESTCASE_DIR"
  {
    echo "# Test Summary"
    echo ""
    echo "Build: PASS"
    echo ""
    echo "No test cases found in \`$TESTCASE_DIR/\`."
  } > "$SUMMARY"
  exit 0
fi

# sort numerically by the N in sample_input_N.txt
IFS=$'\n' INPUTS=($(printf '%s\n' "${INPUTS[@]}" | awk -F'sample_input_|\\.txt' '{print $2 "\t" $0}' | sort -n | cut -f2))
unset IFS

# ---- run each case ----
PASS=0
FAIL=0
declare -a ROWS=()

# FAIL-only debug artifacts are dropped here. Cleared each run (idempotent).
DEBUG_DIR="$WORKSPACE/.debug"
rm -rf "$DEBUG_DIR"

save_debug() {
  # save_debug <N> <input> <actual> <stderr> [expected]
  mkdir -p "$DEBUG_DIR"
  cp "$2" "$DEBUG_DIR/input_${1}.txt"
  cp "$3" "$DEBUG_DIR/my_output_${1}.txt"
  [[ -s "$4" ]] && cp "$4" "$DEBUG_DIR/stderr_${1}.txt"
  if [[ $# -ge 5 && -f "$5" ]]; then
    diff -u "$5" "$3" > "$DEBUG_DIR/diff_${1}.txt" || true
  fi
}

for INPUT in "${INPUTS[@]}"; do
  BASE=$(basename "$INPUT")
  N="${BASE#sample_input_}"; N="${N%.txt}"
  EXPECTED="$TESTCASE_DIR/sample_output_${N}.txt"
  ACTUAL=$(mktemp)
  STDERR=$(mktemp)

  run_with_timeout "$TIMEOUT_SEC" "$BINARY" < "$INPUT" > "$ACTUAL" 2> "$STDERR"
  RC=$?

  LABEL="sample_${N}"

  if [[ $RC -eq 124 || $RC -eq 142 ]]; then
    echo "${RED}[TEST ${N}]${RESET} $LABEL ... FAIL (timeout ${TIMEOUT_SEC}s)"
    save_debug "$N" "$INPUT" "$ACTUAL" "$STDERR"
    ROWS+=("| ${N} | ${LABEL} | FAIL (TLE) |")
    FAIL=$((FAIL+1))
  elif [[ $RC -ne 0 ]]; then
    echo "${RED}[TEST ${N}]${RESET} $LABEL ... FAIL (exit ${RC})"
    [[ -s "$STDERR" ]] && sed 's/^/  /' "$STDERR" | head -5
    save_debug "$N" "$INPUT" "$ACTUAL" "$STDERR"
    ROWS+=("| ${N} | ${LABEL} | FAIL (RTE exit ${RC}) |")
    FAIL=$((FAIL+1))
  elif [[ ! -f "$EXPECTED" ]]; then
    echo "${YELLOW}[TEST ${N}]${RESET} $LABEL ... no expected output (skipped compare)"
    save_debug "$N" "$INPUT" "$ACTUAL" "$STDERR"
    ROWS+=("| ${N} | ${LABEL} | SKIP (no expected) |")
  else
    # exact match after stripping trailing whitespace per line
    if diff -q <(sed 's/[[:space:]]*$//' "$EXPECTED") <(sed 's/[[:space:]]*$//' "$ACTUAL") > /dev/null; then
      echo "${GREEN}[TEST ${N}]${RESET} $LABEL ... PASS"
      ROWS+=("| ${N} | ${LABEL} | PASS |")
      PASS=$((PASS+1))
    else
      echo "${RED}[TEST ${N}]${RESET} $LABEL ... FAIL"
      echo "${BOLD}  --- diff (expected vs got) ---${RESET}"
      diff -u "$EXPECTED" "$ACTUAL" | sed 's/^/  /' | head -30
      echo "${BOLD}  --- debug files: $DEBUG_DIR/ ---${RESET}"
      save_debug "$N" "$INPUT" "$ACTUAL" "$STDERR" "$EXPECTED"
      ROWS+=("| ${N} | ${LABEL} | FAIL |")
      FAIL=$((FAIL+1))
    fi
  fi

  rm -f "$ACTUAL" "$STDERR"
done

TOTAL=$((PASS+FAIL))
echo ""
echo "${BOLD}${PASS}/${TOTAL} passed${RESET}"

# ---- write summary.md ----
{
  echo "# Test Summary"
  echo ""
  echo "Build: ${BUILD_STATUS}"
  echo ""
  echo "| # | Test Case | Result |"
  echo "|---|-----------|--------|"
  for ROW in "${ROWS[@]}"; do
    echo "$ROW"
  done
  echo ""
  echo "${PASS}/${TOTAL} passed"
  if [[ -d "$DEBUG_DIR" ]]; then
    echo ""
    echo "Debug artifacts for failing cases: \`workspace/.debug/\`"
  fi
} > "$SUMMARY"

[[ $FAIL -eq 0 ]] && exit 0 || exit 1
