"""
Stdlib-only fallback for tools/gen_bg.py — talks to the Gemini image model
over plain HTTPS so it works even when pip / google-genai are unavailable.

Usage:
    python tools/gen_img_rest.py <output_name> --prompt-file p.txt --sprites --ref a.png --ref b.png
    python tools/gen_img_rest.py <output_name> "prompt text" [--sprites] [--ref img]...

Env: GEMINI_API_KEY required.
Output: REFACTOR/game/images/sprites/<name>.png  (--sprites)  or  .../backgrounds/<name>.jpg
"""
import argparse, base64, json, mimetypes, os, sys, urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BG_DIR = REPO_ROOT / "REFACTOR" / "game" / "images" / "backgrounds"
SPRITES_DIR = REPO_ROOT / "REFACTOR" / "game" / "images" / "sprites"
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("prompt", nargs="?", default=None)
    p.add_argument("--prompt-file", type=Path)
    p.add_argument("--ref", action="append", type=Path, default=[])
    p.add_argument("--sprites", action="store_true")
    p.add_argument("--model", default=MODEL)
    args = p.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); return 1
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt
    if not prompt:
        print("ERROR: need a prompt or --prompt-file", file=sys.stderr); return 1

    parts = [{"text": prompt}]
    for ref in args.ref:
        if not ref.exists():
            print(f"ERROR: ref not found: {ref}", file=sys.stderr); return 1
        mt = mimetypes.guess_type(str(ref))[0] or "image/png"
        parts.append({"inlineData": {"mimeType": mt, "data": base64.b64encode(ref.read_bytes()).decode()}})

    body = json.dumps({"contents": [{"parts": parts}]}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent?key={key}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr); return 1

    out_dir = SPRITES_DIR if args.sprites else BG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "png" if args.sprites else "jpg"
    out_path = out_dir / f"{args.name}.{ext}"

    cand = (payload.get("candidates") or [{}])[0]
    wrote = False
    for part in cand.get("content", {}).get("parts", []):
        if "text" in part and part["text"].strip():
            print(f"[model] {part['text'].strip()}")
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            out_path.write_bytes(base64.b64decode(inline["data"]))
            print(f"wrote {out_path.relative_to(REPO_ROOT)} ({out_path.stat().st_size} bytes)")
            wrote = True
    if not wrote:
        print("no image in response:\n" + json.dumps(payload, indent=2)[:2000], file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
