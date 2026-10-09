#!/bin/bash
# Static analysis only, in ephemeral CI scratch; never run or publish game code.
set -euo pipefail
ROOT="${GITHUB_WORKSPACE:?}"
LOG="$PWD/input-apple-verification.txt"
SCRATCH=$(mktemp -d "${RUNNER_TEMP:?}/spicy-input.XXXXXX")
trap 'rm -rf "$SCRATCH"' EXIT
{
  echo "Source: $GITHUB_SHA; run: $GITHUB_RUN_ID"
  echo 'Method: shasum, unzip CRC/extraction, lipo, otool, codesign (no execution)'
  before=$(shasum -a 256 "$ROOT/pool8Signed.ipa" | cut -d' ' -f1)
  echo "input_sha256_before=$before"
  test "$before" = '6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84'
  unzip -tq "$ROOT/pool8Signed.ipa"
  unzip -q "$ROOT/pool8Signed.ipa" -d "$SCRATCH"
  APP="$SCRATCH/Payload/pool.app"
  lipo -archs "$APP/pool"
  otool -hv "$APP/pool"
  otool -L "$APP/pool"
  echo '### Apple code-signature verification of ORIGINAL INPUT (not release signing)'
  set +e
  codesign --verify --deep --strict --verbose=4 "$APP"
  status=$?
  set -e
  echo "input_codesign_verify_exit=$status"
  echo 'Nonzero means the input signature failed; it does not fail the independent component job.'
  after=$(shasum -a 256 "$ROOT/pool8Signed.ipa" | cut -d' ' -f1)
  echo "input_sha256_after=$after"
  test "$before" = "$after"
} 2>&1 | tee "$LOG"
