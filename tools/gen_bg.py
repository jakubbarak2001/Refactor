"""
Generate a REFACTOR background via Google AI Studio (Nano Banana 2).

Usage:
    python tools/gen_bg.py <output_name> "<prompt>"
    python tools/gen_bg.py <output_name> --prompt-file path/to/prompt.txt
    python tools/gen_bg.py <output_name> "<prompt>" --variants 4
    python tools/gen_bg.py <output_name> "<prompt>" --model <override>
    python tools/gen_bg.py <output_name> --prompt-file p.txt --ref a.jpg --ref b.jpg

Reference images (--ref) are sent multimodally so the model can copy their
style. Without --ref, "match the style of X.jpg" in the prompt is just text
the model can't see.

Env:
    GEMINI_API_KEY  required (get one at https://aistudio.google.com/apikey)

Output:
    REFACTOR/game/images/backgrounds/<output_name>.jpg
    With --variants N>1: <output_name>_1.jpg ... <output_name>_N.jpg
"""

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path

import PIL.Image
from google import genai

REPO_ROOT = Path(__file__).resolve().parent.parent
BG_DIR = REPO_ROOT / "REFACTOR" / "game" / "images" / "backgrounds"
SPRITES_DIR = REPO_ROOT / "REFACTOR" / "game" / "images" / "sprites"
CARDS_DIR = REPO_ROOT / "REFACTOR" / "game" / "images" / "cards"

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"


def generate(client: genai.Client, model: str, prompt: str, out_path: Path, refs: list[Path] | None = None) -> None:
    contents: list = [prompt]
    if refs:
        for ref in refs:
            contents.append(PIL.Image.open(ref))
    response = client.models.generate_content(model=model, contents=contents)
    saved = False
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(f"[model] {part.text.strip()}")
        elif part.inline_data is not None:
            raw = PIL.Image.open(BytesIO(part.inline_data.data))
            if out_path.suffix.lower() == ".png":
                raw.save(out_path, "PNG")
            else:
                raw.convert("RGB").save(out_path, "JPEG", quality=92)
            print(f"wrote {out_path.relative_to(REPO_ROOT)}  ({raw.size[0]}x{raw.size[1]})")
            saved = True
    if not saved:
        raise RuntimeError("no image returned")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("name", help="output filename without extension, e.g. police_station_colonel_office")
    p.add_argument("prompt", nargs="?", default=None)
    p.add_argument("--prompt-file", type=Path)
    p.add_argument("--variants", type=int, default=1)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--ref", action="append", type=Path, default=[],
                   help="reference image path(s) for style transfer; pass --ref multiple times")
    p.add_argument("--sprites", action="store_true",
                   help="output to sprites/ folder instead of backgrounds/ (and save as PNG, not JPG)")
    p.add_argument("--cards", action="store_true",
                   help="output to images/cards/ as PNG (battle_card_view picks these up by card_id filename)")
    args = p.parse_args()

    for ref in args.ref:
        if not ref.exists():
            p.error(f"reference image not found: {ref}")

    if not args.prompt and not args.prompt_file:
        p.error("provide a prompt arg or --prompt-file")
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set. Get one at https://aistudio.google.com/apikey", file=sys.stderr)
        print("Then in PowerShell:  setx GEMINI_API_KEY \"your-key\"  (restart shell after)", file=sys.stderr)
        return 1

    if args.cards:
        out_dir, ext = CARDS_DIR, "png"
    elif args.sprites:
        out_dir, ext = SPRITES_DIR, "png"
    else:
        out_dir, ext = BG_DIR, "jpg"
    out_dir.mkdir(parents=True, exist_ok=True)
    client = genai.Client(api_key=api_key)

    if args.variants <= 1:
        generate(client, args.model, prompt, out_dir / f"{args.name}.{ext}", args.ref)
    else:
        for i in range(1, args.variants + 1):
            generate(client, args.model, prompt, out_dir / f"{args.name}_{i}.{ext}", args.ref)
    return 0


if __name__ == "__main__":
    sys.exit(main())
