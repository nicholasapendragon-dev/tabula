#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/dist"
OUT_FILE="$OUT_DIR/tabula-android-tablet.zip"

mkdir -p "$OUT_DIR"
rm -f "$OUT_FILE"

cd "$ROOT_DIR"
zip -r "$OUT_FILE" android-tablet \
  -x "android-tablet/.gradle/*" \
  -x "android-tablet/build/*" \
  -x "android-tablet/app/build/*"

echo "Created: $OUT_FILE"
