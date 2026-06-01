"""
Idempotent art-fill driver for REFACTOR relic icons + the contemplative-JB sprite.

gen_bg.py has no retry, so a single Gemini 503 ("high demand") aborts a whole
--variants N group. This driver generates ONE variant per call, SKIPS variants
that already exist on disk, and retries transient 5xx with exponential backoff.
Safe to re-run any number of times — it only fills the gaps.

    python tools/gen_art_retry.py            # fill all missing relic + JB variants
    python tools/gen_art_retry.py --relics-only
    python tools/gen_art_retry.py --jb-only
"""
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RELICS_DIR = REPO / "REFACTOR" / "game" / "images" / "relics"
SPRITES_DIR = REPO / "REFACTOR" / "game" / "images" / "sprites"
PROMPTS = REPO / "tools" / "prompts"

RELICS = [
    "service_pistol", "lucky_koruna", "taser", "red_bull_crate", "golden_handcuffs",
    "protein_tub", "weightlifting_belt", "gym_keycard", "barbell",
    "the_dartboard", "brass_knuckles", "colonel_mugshot", "confiscated_vial",
    "rubber_duck", "evidence_bag", "cold_case_file", "cracked_laptop",
]
RELIC_VARIANTS = 2

JB_PROMPTS = ["jb_contemplative_v1", "jb_contemplative_v2", "jb_contemplative_v3"]
JB_VARIANTS = 2
JB_REFS = [
    SPRITES_DIR / "jb_neutral.png",
    SPRITES_DIR / "jb_developer_call.png",
]

MAX_RETRIES = 5
BACKOFF = [5, 10, 20, 40, 60]


def gen_one(name, prompt_file, out_dir, kind_flag, refs=None):
    """Generate a single image as <name>.png; retry transient failures."""
    out = out_dir / f"{name}.png"
    if out.exists():
        print(f"  skip  {name} (exists)")
        return True
    cmd = [sys.executable, str(REPO / "tools" / "gen_bg.py"), name,
           "--prompt-file", str(prompt_file), kind_flag, "--variants", "1"]
    for r in refs or []:
        cmd += ["--ref", str(r)]
    for attempt in range(MAX_RETRIES):
        try:
            res = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=180)
            if res.returncode == 0 and out.exists():
                print(f"  OK    {name}")
                return True
            err = (res.stderr or res.stdout or "").strip().splitlines()
            tail = err[-1] if err else "no output"
            print(f"  retry {name} (attempt {attempt + 1}): {tail[:120]}")
        except subprocess.TimeoutExpired:
            print(f"  retry {name} (attempt {attempt + 1}): timeout")
        if attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF[min(attempt, len(BACKOFF) - 1)])
    print(f"  FAIL  {name} (exhausted retries)")
    return False


def main():
    do_relics = "--jb-only" not in sys.argv
    do_jb = "--relics-only" not in sys.argv
    ok = fail = 0

    if do_relics:
        print("=== RELICS ===")
        for rid in RELICS:
            pf = PROMPTS / f"relic_{rid}.txt"
            if not pf.exists():
                print(f"  MISS prompt {pf.name}")
                continue
            for n in range(1, RELIC_VARIANTS + 1):
                (ok, fail) = (ok + 1, fail) if gen_one(f"{rid}_{n}", pf, RELICS_DIR, "--relics") else (ok, fail + 1)

    if do_jb:
        print("=== JB CONTEMPLATIVE ===")
        for base in JB_PROMPTS:
            pf = PROMPTS / f"{base}.txt"
            if not pf.exists():
                print(f"  MISS prompt {pf.name}")
                continue
            for n in range(1, JB_VARIANTS + 1):
                (ok, fail) = (ok + 1, fail) if gen_one(f"{base}_{n}", pf, SPRITES_DIR, "--sprites", JB_REFS) else (ok, fail + 1)

    print(f"=== DONE  generated/ok={ok}  failed={fail} ===")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
