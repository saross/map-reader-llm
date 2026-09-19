#!/usr/bin/env bash
# Gemini 3.7 image, 55-map: unions, provenance sidecars, crops, arms.
#
# Since 2026-09-19 a thin wrapper over the campaign-generic
# scripts/image-55map-unions-and-arms.sh (CAMPAIGN=g37). It keeps this
# entry point's original defaults — rungs "1 3" and both arms on realtime
# flex, the route the committed K = 1 and K = 3 legs ran — so a re-run
# reproduces what the campaign record describes. The K = 5 rung was run
# through it on 2026-09-17/18 with KS=5. For anything new, call the generic
# script directly; the PI ruling of 2026-09-18 puts 3.7 legs on batch.
#
# Usage:
#     bash scripts/gemini37-image-55map-unions-and-arms.sh
#     KS=5 WORKERS=50 bash scripts/gemini37-image-55map-unions-and-arms.sh
#
# Created: 2026-09-13; wrapper since 2026-09-19
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
set -euo pipefail
cd "$(dirname "$0")/.."
CAMPAIGN=g37 KS="${KS:-1 3}" ARM1_MODE="${ARM1_MODE:-realtime}" ARM2_MODE="${ARM2_MODE:-realtime}" \
  exec bash scripts/image-55map-unions-and-arms.sh "$@"
