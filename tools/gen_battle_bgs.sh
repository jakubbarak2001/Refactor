#!/usr/bin/env bash
# Generate all battle-ladder backgrounds (10 enemies x 3 prompts x 3 variants = 90).
# Runs gen_img_rest.py in batches of 5 to stay under rate limits.
set -u

cd "$(dirname "$0")/.."
mkdir -p tools/logs

ENEMIES=(rvac sprejeri fanousek spis nguyen varic pastyrak dispatcher inspekce garda)
LETTERS=(a b c)
VARIANTS=(1 2 3)

REFS=(
  --ref REFACTOR/game/images/backgrounds/cafe.jpg
  --ref REFACTOR/game/images/backgrounds/police_station_interior.jpg
  --ref REFACTOR/game/images/backgrounds/police_parking_lot.jpg
)

PARALLEL=5
N=0
TOTAL=0
SKIPPED=0

for e in "${ENEMIES[@]}"; do
  for L in "${LETTERS[@]}"; do
    for v in "${VARIANTS[@]}"; do
      OUT="REFACTOR/game/images/backgrounds/bg_${e}_${L}_${v}.jpg"
      TOTAL=$((TOTAL + 1))
      if [ -f "$OUT" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
      fi
      python tools/gen_img_rest.py "bg_${e}_${L}_${v}" \
        --prompt-file "tools/prompts/bg_${e}_${L}.txt" \
        "${REFS[@]}" \
        > "tools/logs/bg_${e}_${L}_${v}.log" 2>&1 &
      N=$((N + 1))
      if [ $((N % PARALLEL)) -eq 0 ]; then
        wait
      fi
    done
  done
done
wait

echo "done. total=$TOTAL skipped(existing)=$SKIPPED launched=$N"
ls -la REFACTOR/game/images/backgrounds/bg_*.jpg 2>/dev/null | wc -l | xargs -I{} echo "bg_*.jpg count: {}"
