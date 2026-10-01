# GPU job A — lyric timing (paste this into Claude Code on the GPU machine)

Repo: `stavrosnco/test`, branch `claude/magical-dirac-ghhsvi`, working folder `build-order/`.

1. Clone (or pull) the repo and check out branch `claude/magical-dirac-ghhsvi`.
2. Copy the Suno WAV of "One More Game" to `build-order/audio/one_more_game.wav`.
   It's large, so add `build-order/audio/*.wav` to `.gitignore` and **don't commit it**. It stays on this machine for the final mux.
3. Make a Python 3.10–3.12 virtualenv with CUDA PyTorch, then `pip install whisperx demucs`.
   ffmpeg must be on PATH. If whisperx pins a torch version that fights CUDA, install whisperx first
   and then reinstall the CUDA torch build that matches the driver (`nvidia-smi`).
4. From `build-order/`, run: `python tools/align_gpu.py audio/one_more_game.wav`
5. Sanity check: `analysis/transcript.txt` should read like the song from about 0:00 to 4:11.
   Fix the script if something breaks, but don't hand-edit the outputs.
6. Commit `analysis/words.json`, `analysis/transcript.txt`, `audio/vocals.mp3` and `audio/instrumental.mp3`
   (not the WAV, not `analysis/demucs/`), then push to `claude/magical-dirac-ghhsvi`.
7. Report back: GPU model, VRAM, OS, and whether ComfyUI is installed. That decides whether job B
   (AI-generated backdrops) is worth doing.
