# "Build Order" — Suno instructions

Paste each block into Suno's **Custom** mode (v4.5+ / v5). Don't put artist or show names in the
style box; Suno filters them. The style text below describes the sound instead.

## Title
Build Order

## Style of Music
```
Broadway hip-hop musical, theatrical fast-paced rap with dense internal rhymes and triplet flows, ensemble choir hooks, call-and-response chants, harpsichord and pizzicato string stabs, punchy boom-bap drums with deep 808s, 90s video game MIDI synths and chiptune accents, war drums, gritty industrial guitar riffs, cinematic orchestral swells, male lead rapper, female featured rapper, spoken-word narrator, 100 BPM with double-time verses, key change on final chorus
```

## Exclude Styles (if your plan has it)
```
country, lo-fi, EDM drop, heavy autotune, trap hi-hat rolls
```

## Lyrics
```
[Intro: Spoken Narrator, plucked strings, ticking clock]
Nineteen ninety-two. A desert world. A spice to mine.
A team out in Vegas drew the blueprint for the grind:
Harvest. Build. Expand. Attack. And do it all in real time.
Thirty years later, we're still running that design.

[Ensemble Chant]
Build order! (Build order!)
Gather and expand!
Build order! (Build order!)
The whole world at your command!

[Verse 1: Male Lead Rapper, fast]
I was ten with a Pentium, a beige tower, modem screamin',
CRT glow on my face till three a.m., still dreamin',
floppy disks in a shoebox, a mouse with a ball inside,
one click and a whole battalion moves, I'm along for the ride!
Dune Two was the founding father, harvesters out on the sand,
a sandworm ate my tank whole and I didn't understand,
but I learned it: you can't win a war if you can't feed it,
gotta mine before you fight, gotta build it 'fore you need it!

[Pre-Chorus: Ensemble, building]
Fog of war on the border, nothing on the map,
just a town hall and a worker and a clock that won't stop...

[Chorus: Full Ensemble, choir and 808s]
One more game! (One more game!)
Mom is yelling down the stairs, but I'm one more game!
Rush 'em, tower, turtle, tech it late,
every empire in history was "one more game!"
One more game! (One more game!)
Sun is coming up and I'm still one more game!
Not gonna stop till the fog of war is lifted,
gimme the map, gimme the mouse, gimme one more game!

[Verse 2: Gruff Male Rapper, war drums, brass]
Ninety-five! Tides of Darkness! Orcs on the shore!
Humans in the castle and we're kicking down the door!
Peons in the gold mine, "Zug zug!", chopping the wood,
chop the whole forest flat 'cause the lumber's looking good!
Ogre-magi bloodlust, catapults up on the hill,
death knights raise the dead and the dead don't stand still,
click a sheep too many times and the sheep goes boom,
that's the kind of game design that'll follow you to the tomb!

[Verse 3: Male Lead Rapper, industrial guitars, aggressive]
[Robotic Female Voice] Construction complete.
Westwood dropped the hammer with a live-action screen,
a bald man in the briefing room, Tiberium glowing green,
"Peace through power!" Brotherhood of Nod,
GDI up in orbit with an ion cannon like a god,
harvester hauling crystals like a cash machine,
Mammoth tanks rolling over everything in between,
engineer slips through the wall in the dead of night,
now your Obelisk is mine and it's firing on your light!
[Robotic Female Voice] Unit ready. Unit lost.
Then Red Alert rewrote the timeline, Tesla coils and Soviet red!

[Verse 4: Female Rapper, harpsichord and strings, regal]
Ninety-seven, Ensemble took the history books for a spin,
Stone Age, Tool Age, Bronze, Iron, let the ages begin!
Villagers on the berries, fishing boats along the coast,
twelve civs of the ancient world, so who's gonna build the most?
Priest in a robe goes "Wololo!" Now your army's mine,
I converted your elephants, crossed the river, held the line,
typed "Photon Man" in the chat, laser trooper in a toga,
then the Age of Kings rolled trebuchets and your castle walls are over!

[Chorus: Full Ensemble]
One more game! (One more game!)
Mom is yelling down the stairs, but I'm one more game!
Rush 'em, tower, turtle, tech it late,
every empire in history was "one more game!"

[Verse 5: Male Lead Rapper and Female Rapper trading lines, fastest flow]
Ninety-eight! Now the sky splits three ways in the dark,
Terran grit! Zerg swarm! Protoss gold and a psionic spark!
"SCV, good to go, sir!" Zerglings, six-pool rush!
Pylon down, you must construct additional... hush!
Not enough minerals! Insufficient vespene gas!
Battle.net past midnight and the ladder is a class,
then Seoul made it a stadium sport, Brood War on TV,
three hundred actions a minute, that's a symphony!
[Robotic Female Voice] Nuclear launch detected.
Find the ghost! Too late!
En Taro Adun, GG, and I'm queuing one more game!

[Bridge: Sung, slower, piano and strings, tender]
We hauled CRTs down the basement stairs,
forty pounds of glass and a tangle of wires,
pizza and a hub that barely worked,
eight kids, one LAN, nobody slept, nobody shirked.
And the games got old, and the pixels faded out,
but every kid who built a base knows what the fight's about:
you gather what you've got, you build it up from none,
and you never, ever quit until the last game's done.

[Final Chorus: Key change, full choir, all voices]
One more game! (One more game!)
Mom is yelling down the stairs, but I'm one more game!
Rush 'em, tower, turtle, tech it late,
every empire in history was "one more game!"
One more game! (One more game!)
Sun is coming up and we're still one more game!
Not gonna stop till the fog of war is lifted,
gimme the map, gimme the mouse, gimme one more game!

[Outro: Call and response, drums drop out]
Build order?
(Workers first!)
Scout the map?
(Find 'em first!)
Hold the line?
(Never break!)
And when it's over?
(One more game.)

[Spoken, quiet] GG.
[End]
```

## Generation tips
- Generate 4–6 takes; pick the one where verses actually go double-time and the chorus
  chant is crisp. Use **Replace Section** to re-roll a weak verse instead of re-rolling everything.
- If the robotic voice lines get rapped instead of spoken, change those tags to
  `[Spoken: robotic female computer voice]`.
- If the whole thing comes back over 4:30, cut the second mid-song chorus.

## What to send back
1. The track as **WAV** (MP3 works, WAV is better for beat detection).
2. **Stems** (vocals / instrumental) if your plan allows. Otherwise I'll split them with Demucs on the GPU.
3. The lyrics **as Suno actually sang them**. It sometimes changes words, and the captions
   need to match the audio.

Easiest handoff: commit them to `build-order/audio/` on this branch, or drop them in Google Drive and tell me the file name.
