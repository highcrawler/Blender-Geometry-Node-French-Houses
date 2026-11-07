#!/usr/bin/env bash
set -euo pipefail
P="$(cd "$(dirname "$0")" && pwd)"
: > "$P/godot_capture.log"
for view in distance300 side detail macro isolated; do
 for variant in A B C; do
  J_VIEW="$view" H_ASSET="beam_${variant}.glb" H_SHOT="$P/screenshots/godot_${variant}_${view}.png" \
   godot --path "$P/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
 done
done
python "$P/make_board.py"
