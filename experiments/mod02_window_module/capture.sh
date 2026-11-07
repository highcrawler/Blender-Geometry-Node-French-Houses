#!/usr/bin/env bash
# Godot 4.7: real 1280x720 screenshots of all three natively imported GLBs.
set -euo pipefail
P="$(cd "$(dirname "$0")" && pwd)"
: > "$P/godot_capture.log"
shot() {
  local variant="$1" view="$2" asset="$3"
  J_VIEW="$view" H_ASSET="$asset" H_SHOT="$P/screenshots/godot_${variant}_${view}.png" \
    godot --path "$P/godot_test" --rendering-driver opengl3 \
      --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
}
for view in side iso detail distance300; do
  shot A "$view" mod02_A_three_plain.glb
  shot B "$view" mod02_B_window_wall.glb
done
for view in window_front window_oblique reveal_detail; do shot B "$view" mod02_B_window_wall.glb; done
for view in single_front single_oblique single_back; do shot C "$view" mod02_C_window_only.glb; done
python "$P/make_board.py"
