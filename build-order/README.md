# One More Game: RTS music video

Pixel-art music video for the Suno track "One More Game" (see `SUNO.md`, `PLAN.md`).

## Layout
- `audio/` track MP3 plus Demucs stems (the WAV stays on the GPU box)
- `analysis/` beats (`beats.json`), WhisperX words (`words.json`), as-sung lyrics, and `timeline.json` (every lyric word timed)
- `tools/` `analyze.py` (beats), `align_gpu.py` (GPU lyric timing), `build_timeline.py` (lyrics + words → timeline)
- `render/` the renderer: 384×216 frames, 5× nearest upscale + CRT pass → 1080p
  - `director.py` maps song time to scenes; one `sc_*.py` per section
  - `engine.py` timeline lookup, HUD themes, portraits, the `MapScene` base class
  - `units.py`, `sprites.py`, `world.py`, `bedroom.py` art

## Render
```
pip install numpy pillow librosa
cd render
python render_clip.py --t0 0 --t1 251.6 --out ../out/one_more_game.mp4      # full video
python render_clip.py --t0 98.9 --t1 124.9 --out ../out/v3.mp4                # one section
python render_clip.py --t0 0 --t1 1 --still 110 --out ../out/frame.png        # one frame
```
For the final master, mux with the WAV instead of the MP3: `--audio audio/one_more_game.wav`.
