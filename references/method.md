# brand-film method

Everything learned making the Solidinput favicon film (2026-11-20). The full working source is `../example/` (13.5 s, 1080×1080, rendered in 12 s on an M3 Pro). Read the example's `compositions/film.html` alongside this file; its sections carry the same headings.

## Setup

```bash
S=<session scratchpad>
cd $S && DO_NOT_TRACK=1 npx hyperframes init <name> --skip-skills
cd <name> && mkdir -p assets/fonts assets/lib assets/audio
curl -s -o assets/lib/gsap.min.js https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js
```

- Point `index.html` at `assets/lib/gsap.min.js`, not the CDN.
- Fonts: fetch the Google Fonts CSS with a desktop Chrome User-Agent (`curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" "https://fonts.googleapis.com/css2?family=..."`), take the `/* latin */` `woff2` URL, download it to `assets/fonts/`. For variable axes (Bitcount's `ELSH`), request the range (`ELSH,wght@0..100,700`) so the file keeps the axis. Declare each with `@font-face` inside the scene's `<template>`.
- Bundled fonts that resolve by name: Inter, JetBrains Mono, IBM Plex Mono, Space Mono and others (see HyperFrames `format.md`). Use JetBrains Mono for URL bars and code.
- Node 22+ and ffmpeg are the only requirements. Python with numpy/scipy only for the score (use a venv in the scratchpad).
- HyperFrames docs live in `github.com/heygen-com/hyperframes/skills/hyperframes/references/` (`format.md`, `runtimes.md`, `motion.md`, `sound.md`, `types/character.md`). Read with `gh api repos/heygen-com/hyperframes/contents/<path> --jq .content | base64 -d`.

## Structure

- `index.html`: root composition `main` (1080×1080, `data-duration` = film length). It mounts one scene `film` from `compositions/film.html` and holds the `<audio id="score">`.
- `compositions/film.html`: everything inside `<template>`, root `#root` with `data-composition-id="film"`. The host id, the scene root id and the timeline key must all be `film`.

## The engine: one clock, one pure render(t)

```js
const clock = { t: 0 };
const tl = gsap.timeline({ paused: true });
tl.fromTo(clock, { t: 0 }, { t: DUR, duration: DUR, ease: "none", onUpdate: () => render(clock.t) }, 0);
render(0);
window.__timelines["film"] = tl;   // register last
```

Every visible thing is computed from `t` alone inside `render(t)`: transforms, opacities, canvas drawings, text swaps. No GSAP tweens on the same elements, no timers, no `Math.random()` (use the seeded `hash(x, y, seed)`). This makes any frame seekable and the render deterministic, and it avoids GSAP `fromTo` ordering bugs across many hops.

## Layout math

- Frame pixels everywhere. The browser window sits at a fixed frame position; the page viewport origin is a constant offset. Write a helper `V(vx, vy)` that turns viewport coords into frame coords, and place every hero landing with it.
- Example numbers: window at (60, 70), 960×940; title bar 48 px with the tab; URL row 44 px; page viewport at (60, 162), 960×848.
- Tab favicon spot: tab left + 12 px, 16 px icon. The hero's feet point when it sits in the tab = icon centre x, icon bottom y.
- Page bands (top to bottom) are absolute boxes in the viewport. Each band starts hidden and is revealed by one landing.

## Hero

- **Rig**: `#hero` (translate to the feet point) › `#hero-size` (uniform scale, origin at the feet) › `#hero-spin` (rotation, origin at the body centre) › `#hero-body` (squash, origin at the feet) › `<svg>`. Set all four with `style.transform` from `render`.
- **Pixel version of a logo**: rasterize the SVG path with `new Path2D(d)` and `ctx.isPointInPath` at each cell centre (8-unit cells on a ~100-unit logo → 12-13 cells wide). Emit one `<rect>` per filled cell, `shape-rendering="crispEdges"`.
- **Face**: two ink rects for eyes on the top bar of the mark, two ink cells as legs under it. Eyes: hidden (scaleY 0.08) until the wake-up beat, blinks at a list of times (scaleY 0.12 for ±0.06 s), look direction from piecewise-linear keys.
- **Outline**: an ink copy of every cell grown by half a cell on each side, drawn behind. Keep it off while the camouflage joke plays, then switch it on with a short flicker. Without it the hero disappears on any ground of its own colour.
- **Size**: 0.155 scale in the tab (16 px), 1.0 on the page.

### Hops (parabolas)

```js
{ t0: take-off, t1: landing (on a beat), a: from, b: to, h: apex height, s0/s1: size, spin: degrees, crouch: anticipation window }
x = lerp(a.x, b.x, u);  y = lerp(a.y, b.y, u) - h * 4 * u * (1 - u);   // u = (t - t0) / (t1 - t0)
```

- Landing squash: `sy *= 1 - 0.3 * exp(-d * 7) * cos(d * 26)` for 0.7 s after `t1`.
- Crouch before take-off: `sy *= 1 - 0.26 * k²` over the last 0.14 s (0.3 s for the first escape).
- Air stretch: `+0.18` right after take-off, `+0.1` just before landing. `sx = sy^-0.6` keeps the volume.
- Back-to-back hops: take off 0.1 s after the previous landing.
- Extras that sell it: knock wiggles inside the tab before the escape, a wobble when balancing on something thin, one front flip (`spin: -360`) on the big ground-pound.

## Hook opening (frame 0 = thumbnail)

Learned on the Din Firmaadresse film (2026-11-21, `../example-reels/`). The first cut opened on the tab and a grey "Loading…" card; the owner said it did not catch the eye on X. The fix below was called "very lovely". Use it by default.

- **Frame 0:** the browser window is hidden (opacity 0), so the frame is only the page ground, a bold two-line hook in the display face (~108 px at 1080 wide, accent colour on the last words) and the hero big under it: tile ~560 px on screen, eyes open from t = 0, legs on. Hook line copy names the joke, not the product: "We gave our logo / a job."
- **0-0.9 s:** the hero lives: one blink (~0.5 s) and the two knock wiggles on beats 0.25 and 0.75 (it taps the glass). Keep the knock sounds.
- **0.9-1.25 s:** the window fades in and rises 70 px into place behind the hero (`opacity` + `translateY` from `t`).
- **0.95-1.4 s:** a first hop `{ a: HOOK, b: TAB, h: 60, s0: BIG, s1: SMALL, sOut: true }`. `sOut` eases the size with `eout` instead of `eio`, so the hero is small before it rises; with `eio` and a high arc the big hero sweeps through the hook line. Keep `h` low (~60).
- **1.3-1.48 s:** the hook line fades and lifts 50 px. It must stay ≥ 1.27 s or `check` flags `line_unread`.
- **1.5 s:** the normal escape hop, crouch shortened to 0.09 s (0.1 s gap after landing in the tab).
- **Camera:** hold the intro zoom (Z2) static from 0 to 1.5 s and ease to the follow camera over 1.5-2.05 s. Put the hero's HOOK position in camera coordinates: `cam = focus + (screen - 540 or 960) / scale`, and size `BIG = tilePx / (104 × scale)`.
- **Layout:** place Z2 so the tab bar sits just below the hook line (Reels: hook top ~296 px, tab top ~520 px on screen). Otherwise the line covers the tab when the window rises.
- **Check:** snapshot 0, 0.75, 1.0, 1.1, 1.2, 1.3, 1.45 s. The hero must never cross the hook line; frame 0 is exported as `thumbnail.png` next to the MP4.

## Square cut (1:1 for X)

Make the vertical master first, then copy the project to `<name>-x` and change these constants (all from the Din Firmaadresse cut, `../example-square/`). Story, timing and sound stay identical, so the same `score.wav` works.

| Where | Vertical (1080×1920) | Square (1080×1080) |
| --- | --- | --- |
| `index.html`: viewport, `body` height, both `data-height` | 1920 | 1080 |
| `film.html`: root `data-height`, `#cam` height | 1920 | 1080 |
| `#hook` top / `#cap` top | 296 px / 296 px | 110 px / 60 px |
| Intro zoom `Z2` (focus x, y, scale) | 330, 560, 2.0 | 330, 440, 2.0 |
| `HOOK` (cam coords) / `BIG` | (330, 705) / 2.69 | (330, 650) / 2.5 |
| `follow(h)` focus y | `960 + 0.55 × (gy + 170 − 960)` | `0.75 × gy + 156` |
| Camera transform centre | `960 − s × fy` | `540 − s × fy` |
| `END` / `END_S` | (540, 854) / 0.82 | (540, 655) / 0.8 |
| Arrow target `tabF.y` | `960 + END_S × (TAB.y − 23 − 854)` | `540 + END_S × (TAB.y − 23 − 655)` |

Rules behind the numbers: `Z2` puts the tab bar just under the hook line; `BIG` makes the tile ~520 px; the follow camera keeps the hero a little below the centre (screen y ~520-730) so the content it lands on stays in view; `END` leaves the top ~260 px for the end line and still shows the payoff (PAID stamp) above the bottom edge. Check with `--safe-zone=standard` (only title-safe warnings remain) and snapshot the same moments as the master.

## Camera

`#cam` wraps the window and the hero; `transform: translate(540 - s*fx, 540 - s*fy) scale(s)` with `transform-origin: 0 0` puts focus point (fx, fy) at the frame centre.

- 0 to 1.5 s: zoomed ×2 on the tab and the placeholder, static, under the hook opening (§Hook opening). The Solidinput film had no hook frame: it zoomed ×2.1-2.2 from 0 to 1.3 s and that tab-only frame was its thumbnail.
- 1.5 to 2.05 s: ease out to the follow camera while the hero leaps.
- Vertical (Reels): the top ~14 % and bottom ~35 % sit under the app's UI. Follow the hero's *ground* y (the lerp between take-off and landing, no arc) with `fy = 960 + 0.55 × (gy + 170 − 960)`, scale 1.0, so the action stays near y 700-1060 and the camera does not bob on jumps.
- Follow: scale 1.03, focus = centre + 10 % of the hero's offset from centre. Subtle life, no seasickness.
- Last 2.5 s: pull back to scale 0.84 to free the top band for the end line.

## Page effects (all from t)

- **Smash**: split the placeholder text into per-letter spans; after the hit each letter flies with a seeded velocity, gravity 1300 px/s² and spin. The viewport's `overflow: hidden` clips the debris.
- **Typing**: per-letter opacity on at `t0 + i * 0.018`, pop from scale 1.5.
- **Drop-in line**: per-letter fall from -80 px with a bounce ease; tween the variable font axis (`font-variation-settings: "ELSH" 0 → 50`) for a pixel-morph.
- **Dither seam**: the site's own 8×8 Bayer algorithm on a canvas, `progress` 0→1 over 0.45 s, accent pixels sprinkled on the boundary.
- **Band fill**: `clip-path: inset(0 0 Hpx 0)` with H rounded to 8 px steps, so it fills in pixel rows.
- **Flood**: 12 px cells revealed by distance from the landing point plus seeded noise.
- **Rise**: an SVG skyline (or any silhouette) translated up in whole-unit steps; lit windows switch on in seeded order 17 ms apart.
- **Ship moment**: the tab label and the URL change (`New Tab` / `localhost:3000` → brand name / real domain) when the hero lands back in the tab.
- **End line**: words pop 0.1 s apart, the URL under it, a pixel arrow drops onto the tab favicon. Hold ≥ 2 s.

## What to swap for a new brand

1. CSS tokens on `#root` (ground, ink, accent, night...) and the two `@font-face` blocks.
2. The hero path string in `buildHero()` and the eye and leg rect positions.
3. Window chrome: title bar style, the three squares, tab label, URL text before and after.
4. Page bands: headline lines, the content band (projects, features, prices), the CTA band, the closing silhouette (Solidinput uses the Tallinn skyline from `src/components/ui/Skyline.tsx`; use something true to the brand).
5. `HOPS`, `BLINKS`, `LOOK` and every `t - <time>` in `render` so each landing reveals its band.
6. End line words and the sub-line URL.
7. `DUR` in the scene and `data-duration` in `index.html` (both places).

## Check and review

- `DO_NOT_TRACK=1 npx hyperframes check` must pass. Expected noise: `composition_file_too_large` (one scene is fine), `escaped_container` for flying debris, overlap info while lines animate in.
- `content_overlap` errors on debris or falling text: add `data-layout-allow-overlap` to that block (not the scene root).
- `text_below_floor`: browser chrome, meta rows and tags are texture; mark their containers `data-layout-ignore`. Real reading text stays ≥ 28 px at 1080.
- `line_unread`: the closing line needs ≥ 2 s on screen.
- Snapshot every landing + 0.1 s, plus 0.05 s and the last frame. Read the contact sheet. First-run catches: hero invisible on its own colour; hero crossing over orange text; end line not pointing at the hero.

## Score (scripts/score.py)

- Chiptune: pulse waves (12.5/25/50 % duty), triangle bass, noise drums, 120 BPM. Intro: hats and a quiet arpeggio only. The groove drops on the first big landing. A riser under the final leap, a major-chord stab when the hero lands home, then a 1.2 s fade.
- One effect per visible action: knock, boing on take-off, soft landing thump, crash with glass pings, key ticks per typed letter, bloops per dropped letter, a sub boom plus a crackle on the ground-pound, rising dings per lit row, a noise swell on the flood, a zap on the outline, stepped notes for the rise, sparkles for windows, a click and pop back in the tab, pops per end-line word.
- The event times in `score.py` are copied from `film.html`. Keep them in step (or move both to one shared JSON if the film grows).
- Mix: `tanh` soft clip, peak-normalise, then `loudnorm=I=-14.5:TP=-1.5:LRA=7`. Target about -15 LUFS integrated, true peak ≤ -1 dBFS.
- Verify: `ffmpeg -i score.wav -af ebur128=peak=true -f null -` and the momentary value every 0.5 s. After the render, `npx hyperframes audio out.mp4 --json` onsets must sit on the landing times.

## Numbers from the first run

13.5 s, 405 frames, 1080×1080 @ 30 fps, 4.4 MB MP4 (h264 + aac). Render 12 s on an Apple M3 Pro, no GPU path tracing. Check: 0 errors, 241/241 text contrast checks pass. Two review rounds (outline, arrow).
