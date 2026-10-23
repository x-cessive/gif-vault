# AGENTS.md — gif-vault

Operating manual for this repo. How the user works in general lives elsewhere;
this file is how work gets done here.

## What this repo is

The single organized home for GIF projects. Projects are strictly separated:
`sovran/` holds sovran-branded sets only; every other project gets its own
top-level folder under `projects/`. Never mix projects in one folder.

## Adding or updating a GIF set

1. New project: `mkdir projects/<project>`. New set: copy
   `projects/_template/` to `projects/<project>/<set-name>/` and fill it in.
2. Put finished GIFs in the set's `gifs/`, sounds (if any) in `sounds/`.
3. Rebuild the gallery: `python3 tools/build_gallery.py` (regenerates `docs/`).
4. Commit everything, including the regenerated `docs/`. Never hand-edit
   `docs/` — it is build output.

## GIF production standard

This is the standing bar for every set in the vault:

- Rig: `tools/office_outfits.py` (shared room + per-state outfit/theme system;
  animators in `tools/office_states_bN.py`; sounds via `tools/gigi_synth_sfx.py`).
- Spec: 128x128 grid, NEAREST x4 to 512x512 square, blocky 8-bit (solid
  colors, no AA, no gradients), 60 unique frames @24fps, seamless infinite loop.
- GIF recipe (exact): `fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer`.
- QC gates (all must pass): <=64 colors; consecutive-pair motion audit at
  32x32 (large majority of pairs active, no slideshow); 18x12
  nearest-neighbor legibility (character + signature colors identifiable);
  contact-sheet eyeball pass.
- Design rules: one constant environment across the set; per-state outfit
  color variation; one signature accent effect per state; real per-frame
  motion everywhere.
- Character rule: Gigi is a river otter. No fox. No dog. An otter.

## Giphy uploads

- `tools/giphy_upload.py` posts a set's GIFs: `GIPHY_API_KEY=... python3
  tools/giphy_upload.py` (key from env only — never commit it).
- It writes `giphy_upload_results.json` (ids + page URLs, no key); keep a copy
  next to the set so the gallery can link each GIF to its Giphy page.
- Free beta keys are rate-limited (~100 calls/hour); the script paces itself.

## Gallery

- `tools/build_gallery.py` scans `projects/*/`, extracts first-frame
  thumbnails, and writes `docs/index.html` (+ `docs/data.json`).
- Published via GitHub Pages from `/docs` on `main`.
- Keep the viewer dependency-free (vanilla HTML/CSS/JS, no build step) so any
  worker can rebuild or patch it.

## Conventions

- File names: `gigi_<set>_<state>.gif` style — lowercase, underscores.
- Sounds are 22050 Hz mono 16-bit WAV, named to match their GIF's state.
- Large binaries belong here (this repo exists for them); never commit large
  binaries to code repos like sovran-cli — stage, QC, then wire via manifest.

---

## UI/UX design

Full library: https://raw.githubusercontent.com/x-cessive/design-library/main/DESIGN_LIBRARY.md

**The rule.** AI output is bounded by reference quality. Never design a UI
from a blank page:
1. Pick 2-3 references from the library before building (galleries for the
   visual bar, pattern libraries for the specific elements).
2. Describe with patterns, not adjectives - link the pattern.
3. If this repo has a design-system doc, it is the source of truth and wins
   over generic references.

**Brand for this repo.** 8-bit GIF standard: 128x128 grid, NEAREST x4 to 512x512, max 64 colors, 60 unique frames @24fps, seamless infinite loop.

**Scope.** Applies to every user-facing surface built from this repo: app
UI, web pages, generated docs/presentations, screenshots. Don't invent
brand silently - propose it in the change and get it reviewed.

---

## Release management

**The rule.** One repo, one canonical checkout per build machine. Stale
duplicate checkouts are how an AI ends up building the wrong thing.

- Canonical checkout on the build machine: TBD — do not assume; if multiple checkouts exist, ask the operator which is canonical.
- Never create suffixed duplicate clones (`-old`, `-backup`, `-copy`,
  `-2`, `-final`, etc.). Scratch copies get deleted when done.
- If you discover multiple checkouts of this repo on the build machine,
  STOP and ask the operator which is canonical. Do not guess.
- Build outputs are versioned artifacts. After a new build is verified
  and pushed, archive superseded builds: move them to
  `_archive/<name>-<date>/`, keep the last 2, older ones may be deleted.
- This section governs hygiene. The repo's own build docs are the
  authority on where artifacts go.


---

## Parallel Worktree Operations (Worktree Fleet)

Adopted 2026-10-22 as a pilot. Fleet kit: x-cessive/worktree-fleet.
Script placement: CENTRAL CLONE, called by path — wt.sh and ralph.sh live in
the worktree-fleet clone (~/workspace/worktree-fleet/ on this VM), they are
not copied into this repo. Coordinator: Boone. Pilot merge policy is set in
the verification gate below.

This repo runs parallel AI agents, one per git worktree. This file is the
contract every agent in this repo follows. The coordinator (human or lead
agent) owns task assignment; worker agents own execution inside their
worktree only.

## Worktree law

- One agent per worktree, one branch per task: `agent/<task-slug>`.
- Never read, edit, or run builds inside another agent's worktree.
- Create and retire worktrees only through `wt.sh` (spawn / done / prune).
- `node_modules`, `target`, `.venv`, `vendor` in a worktree are symlinks to
  the main checkout's shared cache. Never commit through them, never delete
  them, never "fix" them from inside a worktree. `wt.sh` writes these names
  to the repo's `info/exclude` at spawn time, so the links never appear in
  git status and cannot be staged by accident.
- Uncommitted work in a worktree is invisible to everyone else. Commit early,
  commit on your own branch.

## Task board

- `TASKS.md` in the repo root is the board. Only the coordinator writes it.
- Entry format: slug, one-line outcome, worktree, status
  (QUEUED / ACTIVE / IN-REVIEW / DONE / KILLED), acceptance test.
- An agent works only the task whose slug matches its worktree.

## Before asking the human

- Read this file, the repo README, and any CONTROL / STATE surfaces first.
- Search the repo's docs and prior task logs for the answer.
- Ask only when the answer is not in the repo or the choice changes scope,
  cost, or a public surface.

## Coordinator: judging agents by their questions

- A structural question (about shape, ownership, interfaces) means the model
  understands the problem. Let it run.
- A confused question on a simple task means the model is too weak for it.
  Reassign the task; do not coach it through.
- A repeated or nonsensical question, or 10 minutes with no commit and no
  clear question, means kill the worktree and reassign. Sunk cost is not a
  reason to keep a lost agent running.

## Verification gate — "done" means proven

- The acceptance test named in TASKS.md defines done. Passing it is the
  evidence; an agent's claim is not.
- Never hardcode, stub, or mock a result to make a test pass. A test that
  cannot fail is worse than no test.
- UI work: screenshot the result and compare it against the spec before
  claiming done.
- CI must be green on the branch before merge. Merge policy: HUMAN MERGES
  ONLY (pilot setting, 2026-10-22 — the coordinator never merges).
  Version tags are always a separate, human-only step.

## Skill upkeep

- Any procedure that has to be explained twice gets written down once:
  into this file, or into a skill doc under `docs/skills/`, in the same
  change that second explanation happened in.
- Weekly, the coordinator reviews merged branches and folds repeated fixes
  into this file. Stale rules get deleted, not worked around.

## Handoff format

Every agent report, completion or blocked, uses this shape:

    CURRENT STATE
    EVIDENCE        (commands run, test output, commit SHAs)
    BLOCKERS
    UNKNOWNS        (stated, never silently filled in)
    NEXT ACTION

## Guardrails

- No production deploys, no credential changes, no network changes from a
  worktree without the human's explicit word.
- A failing loop stops at its iteration cap and reports. It does not widen
  its own scope, retry forever, or spawn helpers outside its worktree.
