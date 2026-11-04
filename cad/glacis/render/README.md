# Glacis render

1. `cd cad/glacis && ../.venv/bin/python render/export_glb.py`: one build. It writes `robot.glb` (one mesh per look:
   panel, frame, loop, underglow, light bar...) and `meta.json` (muzzles, vents), checks the light bar for clashes,
   exports the Onshape STEPs, rolls up the parts and test-fits the EVIL ENERGY tank (`tankfit.json`).
2. `python3 render/serve.py`, then open http://127.0.0.1:8765/render.html. The page renders once and POSTs
   `render.png` back into this folder. URL switches: `smoke=0`, `glow`, `bloom`, `exp`, camera `cx cy cz` / target
   `tx ty tz`, `out=<name>.png`.
3. For a photo look, give that PNG to Codex image generation as the reference (see the memory note in Claude's
   project memory, or `docs/glacis/render_d1_1_photo.png` for the result).

`robot.glb` and the PNGs here are build output (gitignored).
