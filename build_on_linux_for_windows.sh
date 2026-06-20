#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$ROOT_DIR/.build-windows"
WINEPREFIX="${WINEPREFIX:-$BUILD_DIR/wineprefix}"
WINEARCH="${WINEARCH:-win64}"
PYTHON_EXE="C:\\Python311\\python.exe"

mkdir -p "$BUILD_DIR"
mkdir -p "$WINEPREFIX"

if ! command -v wine >/dev/null 2>&1; then
  echo "wine is not installed"
  exit 1
fi

if ! command -v wineboot >/dev/null 2>&1; then
  echo "wineboot is not installed"
  exit 1
fi

export WINEPREFIX
export WINEARCH

wineboot -u >/dev/null

if [ ! -f "$WINEPREFIX/drive_c/Python311/python.exe" ]; then
  cat <<'EOF'
Windows Python 3.11 is not installed in this Wine prefix.
Install it first, then rerun this script.

Suggested flow:
  1. Download the Windows x64 installer for Python 3.11
  2. Run it through Wine
  3. Make sure it is installed to C:\Python311
EOF
  exit 1
fi

wine "$PYTHON_EXE" -m pip install --upgrade pip
wine "$PYTHON_EXE" -m pip install --upgrade pygame pyinstaller

cd "$ROOT_DIR"
rm -rf build dist atom.spec

wine "$PYTHON_EXE" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name atom \
  main.py

echo "Build finished: $ROOT_DIR/dist/atom.exe"
