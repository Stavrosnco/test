# "Build Order" — animation plan

## Look
Original 16-bit pixel art, isometric RTS battlefield. The whole video sits inside a fake 90s
RTS HUD: minimap, resource counters that tick on the beat, a command card, and green
drag-select boxes. Each verse is a "campaign chapter" with its own palette and terrain.

All art is original and only *evokes* each game. No ripped sprites, logos or likenesses.
That keeps it legally clean and visually consistent.

| Section | Chapter look |
|---|---|
| Intro / V1 (Dune II, the kid) | Bedroom CRT pushes in through the screen into an ochre desert, harvesters, a sandworm |
| V2 (Warcraft II) | Green fantasy forest, gold mine, orcs vs. castle, exploding sheep |
| V3 (C&C / Red Alert) | Grey industrial base, glowing green crystals, FMV-style "briefing" with an original villain, Tesla arcs |
| V4 (Age of Empires) | Warm Mediterranean map, age-up transitions (Stone → Iron), robed priest "conversion" wave |
| V5 (StarCraft) | Deep-space purple, three-faction split screen, swarm rush, nuke-dot countdown |
| Bridge | Back to the basement LAN party, warm and low-key, CRT glow |
| Final chorus / outro | All five chapters' armies on one giant map, fog of war lifts, "GG" |

Lyrics show up as kinetic type styled like in-game chat and unit-acknowledgement text, timed to each word.

## Pipeline
1. **Audio analysis** (here, CPU): librosa for tempo, beats, downbeats, section boundaries and energy curves. Everything animates off this timeline.
2. **Lyric alignment** (local GPU): Demucs vocal isolation, then WhisperX word-level forced alignment against the lyric sheet. Output is `words.json`.
3. **Art** (local GPU, optional): Flux/SDXL with a pixel-art LoRA for backdrops and concept art, then palette-quantized and cleaned so it reads as real pixel art. Units, HUD and effects are drawn in code.
4. **Renderer** (here): a Python engine that renders at 480×270 and upscales nearest-neighbour to 1080p/4K, driven by a scene/timeline script keyed to beats and words. CPU-friendly; frames are deterministic and resumable.
5. **Encode**: ffmpeg (NVENC on the GPU box if we want a fast 4K master).

## GPU jobs (sent to the local Claude when the track is ready)
- Job A: Demucs + WhisperX alignment → `words.json` (needed)
- Job B: backdrop/concept generation batch (optional)
- Job C: final 4K encode (optional)
