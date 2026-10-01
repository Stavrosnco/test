"""Rough CPU transcription with word timestamps (draft only; GPU WhisperX pass replaces it)."""
import json, sys
from faster_whisper import WhisperModel

src = sys.argv[1] if len(sys.argv) > 1 else "audio/one_more_game.mp3"
size = sys.argv[2] if len(sys.argv) > 2 else "small.en"
prompt = open("analysis/lyrics_embedded.txt").read()
prompt = " ".join(l for l in prompt.splitlines() if not l.startswith("["))[-800:]
model = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=4)
segs, _ = model.transcribe(src, word_timestamps=True, vad_filter=False, initial_prompt=prompt,
                           condition_on_previous_text=False)
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
    print(f"{s.start:6.1f}-{s.end:6.1f} {s.text.strip()}", flush=True)
json.dump(out, open(f"analysis/transcript_{size}.json", "w"), indent=1)
