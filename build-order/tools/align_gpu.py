"""GPU job A: vocal isolation + word-level lyric timestamps.

Usage:  python tools/align_gpu.py audio/one_more_game.wav
Writes: analysis/words.json, analysis/transcript.txt, audio/vocals.mp3, audio/instrumental.mp3
"""
import json, subprocess, sys
from pathlib import Path
import torch, whisperx

src = Path(sys.argv[1])
device = "cuda" if torch.cuda.is_available() else "cpu"
assert device == "cuda", "No CUDA device visible to torch"

sep = Path("analysis/demucs")
subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs_ft",
                "-o", str(sep), str(src)], check=True)
stem_dir = sep / "htdemucs_ft" / src.stem
vocals = stem_dir / "vocals.wav"

for name, wav in [("vocals", vocals), ("instrumental", stem_dir / "no_vocals.wav")]:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "192k",
                    f"audio/{name}.mp3"], check=True)

lyrics = " ".join(l for l in Path("analysis/lyrics_embedded.txt").read_text().splitlines()
                  if l and not l.startswith("["))
audio = whisperx.load_audio(str(vocals))
model = whisperx.load_model("large-v3", device, compute_type="float16", language="en",
                            asr_options={"initial_prompt": lyrics[-900:]})
result = model.transcribe(audio, batch_size=16, language="en")
align_model, meta = whisperx.load_align_model(language_code="en", device=device)
result = whisperx.align(result["segments"], align_model, meta, audio, device)

segs = [{"start": s.get("start"), "end": s.get("end"), "text": s["text"].strip(),
         "words": [{"w": w["word"], "s": w.get("start"), "e": w.get("end"), "p": w.get("score")}
                   for w in s.get("words", [])]} for s in result["segments"]]
Path("analysis/words.json").write_text(json.dumps(segs, indent=1))
Path("analysis/transcript.txt").write_text(
    "\n".join(f"{s['start']:7.2f}  {s['text']}" for s in segs if s["start"] is not None))
print(f"{len(segs)} segments, {sum(len(s['words']) for s in segs)} words")
