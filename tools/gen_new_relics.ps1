# Generates icons for the 20 expansion-pool relics, matching the existing
# relic-icon style block (worn object, dark low-key, muted, no text).
# Writes a prompt file per relic to tools/prompts/relic_<id>.txt, then calls
# gen_bg.py --relics (uses the global python that has google-genai).

$ErrorActionPreference = "Stop"
$root = "C:\Users\USER\PycharmProjects\Refactor"
$prompts = "$root\tools\prompts"
$cards = "$root\REFACTOR\game\images\relics"

$style = @"
Editorial-illustration style game relic icon, square 1:1 framing. A single worn object, centered and filling most of the frame, three-quarter view, with a strong readable silhouette. Dramatic low-key lighting and a warm rim-light separating the object from a dark, softly vignetted neutral background (deep charcoal with a faint institutional-green undertone). Muted desaturated palette: institutional green, beige, nicotine-yellow, gunmetal grey. Heavy film grain and scuffed print texture, like a worn trading-card relic. The object is real and used, a possession, not a clean product shot. No text, no logos, no lettering, no numbers, no UI, no border. Painterly, cinematic, melancholic, darkly funny.
"@

$relics = [ordered]@{
  "turkish_coffee"   = "A dented steel vacuum thermos, the screw-cup missing, the metal stained dark where coffee always overflows."
  "kevlar_surplus"   = "A surplus kevlar vest, ballistic panels sagging, straps frayed, the canvas faded and salt-stained at the shoulders."
  "stab_vest"        = "A black police stab-vest on a hook, the front peppered with little blade nicks and scuffs, velcro worn furry."
  "riot_shield"      = "A scratched transparent polycarbonate riot shield gone milky with use, one corner cracked and wrapped in tape."
  "police_flashlight"= "A long aluminium four-cell police flashlight, the anodizing rubbed to bare metal at the grip, lens scratched."
  "mini_fridge"      = "A scuffed break-room mini-fridge, door ajar, a single cold drink can glowing faintly inside, magnets on the door."
  "cop_pension"      = "A creased official pension statement on cheap paper, paper-clipped to a worn payslip, an embossed stamp smudged in the corner."
  "fixer_card"       = "A plain matte-black business card lying on dark wood, blank, edges gone soft from years in a wallet, a faint thumb-smudge across it."
  "spiral_notebook"  = "A bent spiral-bound pocket notebook, cover scuffed, the wire spiral crushed flat at one corner, page edges curled."
  "pawn_receipt"     = "A flimsy carbon-copy pawn-shop receipt creased into quarters, ink faded to nothing, a rubber-stamp smear across one corner."
  "creatine"         = "An open tub of unflavoured creatine monohydrate, the scoop half-buried, white powder dusting the rim, label scuffed blank."
  "chalk_bag"        = "A climber's chalk bag, drawstring open, white magnesium dust caked on the canvas and smeared in fingerprints."
  "resistance_bands" = "A tangle of looped rubber resistance bands, one frayed nearly to snapping, the rubber gone chalky and pale."
  "posing_trunks"    = "A pair of sequined bodybuilding posing trunks, garish blue gone a little tarnished, draped over the end of a worn gym bench."
  "pre_workout"      = "A black unmarked tub of pre-workout powder, lid askew, vivid blue powder spilling out, a hazard-orange scoop beside it."
  "punching_bag"     = "A heavy punching bag patched with electrical tape, a split seam leaking sand, the hanging chain rusted, slightly crooked."
  "knuckle_tape"     = "A half-used roll of white hand-wrap boxing tape, the loose end dangling, the edges grimy from the gym floor."
  "trenbolone"       = "A small amber glass veterinary vial of oil with a rubber-stopper top and a blank scuffed label, a used syringe lying beside it."
  "weighted_vest"    = "A heavy weighted training vest, sand pockets bulging, the canvas faded, straps cinched tight, sitting heavy on a concrete floor."
  "service_photo"    = "A creased academy graduation photograph, a young uniformed officer in the front row, colors faded, one corner dog-eared, the face turned slightly away."
}

$refs = @("$cards\protein_tub.png", "$cards\brass_knuckles.png", "$cards\rubber_duck.png")

foreach ($id in $relics.Keys) {
  $file = "$prompts\relic_$id.txt"
  $body = $style + "`r`n`r`n" + $relics[$id]
  Set-Content -Path $file -Value $body -Encoding UTF8
  Write-Output "=== $id ==="
  & python "$root\tools\gen_bg.py" $id --relics --prompt-file $file --ref $refs[0] --ref $refs[1] --ref $refs[2]
}
Write-Output "DONE"
