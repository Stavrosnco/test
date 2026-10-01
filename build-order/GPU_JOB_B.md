# GPU job B: three backdrop plates (paste this into Claude Code on the GPU machine)

Repo `stavrosnco/test`, branch `claude/magical-dirac-ghhsvi`, folder `build-order/`. Pull first.

## Goal
Generate three still images with ComfyUI + **FLUX.2 Klein 4B fp8** (the distilled `flux-2-klein-4b-fp8`,
not the base model). The cloud side will downscale, quantize and animate them, so you only make the raw images.
Don't pixelate or stylise them yourself.

| name | size (px) | what it is |
|---|---|---|
| `fmv_general` | 1040 × 624 | "live-action" briefing still #1 |
| `fmv_bald` | 1040 × 624 | "live-action" briefing still #2 |
| `stadium` | 1536 × 640 | wide esports arena plate |

## Prompts (use verbatim; no negative prompt needed)
**fmv_general**
> Still frame from a 1995 PC game full-motion-video cutscene. A live-action actor plays a stern military general in an olive-green uniform and beret, seated at a desk in a low-budget sci-fi command center, glowing green tactical monitors behind him. Medium close-up, centered, facing the camera, dim cinematic lighting, slight chroma-key look, VHS tape grain. No text, no logos, no watermark.

**fmv_bald**
> Still frame from a 1995 PC game full-motion-video cutscene. A live-action actor plays a charismatic bald, clean-shaven cult leader in a black high-collared coat, standing in a dark briefing room lit by dramatic red rim light, confident menacing half-smile. Medium close-up, centered, facing the camera, low-budget sci-fi set, VHS tape grain. No text, no logos, no watermark.

**stadium**
> Wide shot from the back of the stands of a packed esports arena in Seoul around 2002. On the stage, two glass soundproof player booths with players at computers; above them, one giant blank glowing blue projection screen. Cheering crowd with light sticks and handmade banners, colorful stage lights cutting through haze. No readable text, no logos, no watermark.

## How
1. Start ComfyUI (the full install at `H:\AI\ComfyUI` is fine). Use the built-in FLUX.2 Klein text-to-image template,
   with the template's default sampler, steps and CFG for the distilled model.
2. Drive it from a script rather than by hand. Export the workflow in **API format**, save it as
   `tools/comfy_flux2_klein_t2i.json`, and write `tools/gen_backdrops.py`, which POSTs to `http://127.0.0.1:8188/prompt`
   with the prompt, size and seed substituted, then downloads the result.
3. Generate **4 seeds per image** (seeds 101–104). Save each as `art/raw/<name>_<seed>.png`.
4. Look at all 12 images. Reject any that:
   - contain readable text, logos or UI;
   - closely resemble a real person or the real 1990s game actors;
   - have extra limbs or mangled hands/faces (fmv);
   - lack the blank screen above the booths (stadium).

   For each name, re-roll with seeds 105+ until you have at least 2 usable images.
5. Write `art/raw/NOTES.md`: one line per image (kept or rejected, and why) and the ComfyUI and model versions.
6. Commit `art/raw/*.png`, `art/raw/NOTES.md`, `tools/gen_backdrops.py` and `tools/comfy_flux2_klein_t2i.json`, then push.
   The images are a few MB each, which is fine.
7. Report back which seed you'd pick for each name.
