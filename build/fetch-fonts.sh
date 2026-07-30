#!/usr/bin/env bash
# Re-download the self-hosted webfonts and regenerate assets/css/fonts.css.
# Run from the repository root. Requires curl + python3.
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CSS_URL="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Jost:wght@300;400;500&family=Kaushan+Script&display=swap"

mkdir -p assets/fonts
curl -sS -A "$UA" "$CSS_URL" -o /tmp/gf.css
python3 build/fetch-fonts.py /tmp/gf.css
