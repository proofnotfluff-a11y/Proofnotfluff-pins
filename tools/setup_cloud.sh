#!/usr/bin/env bash
# Installs what tools/check_repo.py needs on a fresh cloud machine (Oct 29, 2026): the video check's planted failures
# need ffmpeg, Tesseract, OpenCV, the font tools and jsonschema; builder contacts use cryptography and openpyxl.
# Safe to run twice: it skips anything already there. check_repo.py runs it by itself when a video tool is missing.
# Same list as .github/workflows/repo-checks.yml. Python packages come from PyPI, programs from apt.
set -u
SUDO=""; [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null && SUDO="sudo"
missing=""
for prog in ffmpeg tesseract; do command -v "$prog" >/dev/null || missing="$missing $prog"; done
if [ -n "$missing" ]; then
  pkgs=""; case "$missing" in *ffmpeg*) pkgs="$pkgs ffmpeg";; esac; case "$missing" in *tesseract*) pkgs="$pkgs tesseract-ocr";; esac
  $SUDO apt-get install -y -qq $pkgs >/dev/null 2>&1 || { $SUDO apt-get update -qq >/dev/null 2>&1 && $SUDO apt-get install -y -qq $pkgs >/dev/null 2>&1; } \
    || echo "setup_cloud: could not install$pkgs with apt"
fi
python3 -c "import cv2, fontTools, brotli, PIL, jsonschema, cryptography, openpyxl" 2>/dev/null || \
  python3 -m pip install --quiet --disable-pip-version-check fonttools brotli pillow jsonschema opencv-python-headless cryptography openpyxl \
    >/dev/null 2>&1 || python3 -m pip install --quiet --disable-pip-version-check --break-system-packages fonttools brotli pillow jsonschema \
    opencv-python-headless cryptography openpyxl >/dev/null 2>&1 || echo "setup_cloud: could not install the Python packages with pip"
for prog in ffmpeg tesseract; do command -v "$prog" >/dev/null || echo "setup_cloud: $prog still missing"; done
python3 -c "import cv2, fontTools, PIL, jsonschema" 2>/dev/null && echo "setup_cloud: ready" || { echo "setup_cloud: Python packages still missing"; exit 1; }
