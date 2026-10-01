"""GPU job B: FLUX.2 Klein 4B (distilled, fp8) backdrop plates via a running ComfyUI server.

Usage:  python tools/gen_backdrops.py [name ...] [--seeds 101-104]
Needs:  ComfyUI on http://127.0.0.1:8188 with the models named in tools/comfy_flux2_klein_t2i.json
Writes: art/raw/<name>_<seed>.png
"""
import argparse, json, time, urllib.parse, urllib.request, uuid
from pathlib import Path

HOST = "http://127.0.0.1:8188"
WORKFLOW = Path("tools/comfy_flux2_klein_t2i.json")
OUT = Path("art/raw")

PLATES = {
    "fmv_general": (1040, 624,
        "Still frame from a 1995 PC game full-motion-video cutscene. A live-action actor plays a stern "
        "military general in an olive-green uniform and beret, seated at a desk in a low-budget sci-fi "
        "command center, glowing green tactical monitors behind him. Medium close-up, centered, facing "
        "the camera, dim cinematic lighting, slight chroma-key look, VHS tape grain. No text, no logos, "
        "no watermark."),
    "fmv_bald": (1040, 624,
        "Still frame from a 1995 PC game full-motion-video cutscene. A live-action actor plays a "
        "charismatic bald, clean-shaven cult leader in a black high-collared coat, standing in a dark "
        "briefing room lit by dramatic red rim light, confident menacing half-smile. Medium close-up, "
        "centered, facing the camera, low-budget sci-fi set, VHS tape grain. No text, no logos, no "
        "watermark."),
    "stadium": (1536, 640,
        "Wide shot from the back of the stands of a packed esports arena in Seoul around 2002. On the "
        "stage, two glass soundproof player booths with players at computers; above them, one giant "
        "blank glowing blue projection screen. Cheering crowd with light sticks and handmade banners, "
        "colorful stage lights cutting through haze. No readable text, no logos, no watermark."),
}


def api(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(HOST + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def generate(name, seed):
    w, h, text = PLATES[name]
    wf = json.loads(WORKFLOW.read_text())
    wf["74"]["inputs"]["text"] = text
    wf["68"]["inputs"]["value"] = w
    wf["69"]["inputs"]["value"] = h
    wf["73"]["inputs"]["noise_seed"] = seed
    wf["9"]["inputs"]["filename_prefix"] = f"backdrops/{name}_{seed}"
    pid = json.loads(api("/prompt", {"prompt": wf, "client_id": str(uuid.uuid4())}))["prompt_id"]

    while True:
        hist = json.loads(api(f"/history/{pid}")).get(pid)
        if hist and hist.get("status", {}).get("completed"):
            break
        if hist and hist.get("status", {}).get("status_str") == "error":
            raise RuntimeError(f"{name} seed {seed}: {hist['status']}")
        time.sleep(0.5)

    img = hist["outputs"]["9"]["images"][0]
    png = api("/view?" + urllib.parse.urlencode(img))
    dst = OUT / f"{name}_{seed}.png"
    dst.write_bytes(png)
    return dst


def seed_range(s):
    a, _, b = s.partition("-")
    return range(int(a), int(b or a) + 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(PLATES))
    ap.add_argument("--seeds", type=seed_range, default=seed_range("101-104"))
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in args.names:
        for seed in args.seeds:
            t = time.time()
            print(f"{generate(name, seed)}  ({time.time() - t:.1f}s)", flush=True)
