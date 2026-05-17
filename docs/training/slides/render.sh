#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v marp >/dev/null 2>&1; then
  if [[ ! -d node_modules/@marp-team ]]; then
    echo "Installing @marp-team/marp-cli locally..."
    npm install --silent @marp-team/marp-cli
  fi
  MARP="$(pwd)/node_modules/.bin/marp"
else
  MARP="marp"
fi

for f in 01-deconstruction 02-risk-audit 03-imitation 04-commercialization; do
  echo "Rendering ${f}.slide.md ..."
  "$MARP" --pdf "${f}.slide.md"
done

echo
echo "Done. Generated:"
ls -1 *.slide.pdf
