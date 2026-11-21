---
name: brand-film
description: Make a short, fun brand character film for social media (Reels, X, TikTok, LinkedIn) where a brand's own logo or favicon comes alive and builds the brand's real website or product screen, one beat-locked hop at a time, in the brand's real visual style. Opens on a scroll-stopping hook frame, ships a 9:16 master plus a 1:1 cut for X, with a synthesized score or effects-only sound. Renders HTML to MP4 locally with HyperFrames in seconds (no After Effects, no Blender, no GPU), then drafts the caption and a "how we made it" thread. Can extend an existing cut with a cinematic reveal and match cuts, or revise a single shot. Use when the user says /brand-film, asks for "a cool video for X", "a Reel for our product", "a launch clip", "make the logo build the site", "a mascot video like the favicon one", or wants another film in this style for any brand, site, product or feature.
---

# brand-film

The default is a 14 s character film: the brand's mark (favicon, logo, mascot) introduces itself big under a hook line, hops into its browser tab, breaks out, smashes a placeholder and builds the real page or product UI. Every hop lands on a beat and changes the screen. It ends on a punchline and the URL. Made as code, rendered in about 10 s on a laptop.

Worked examples (read the one closest to the brief):

| Folder | Film | Format | Hero | Sound |
| --- | --- | --- | --- | --- |
| `example/` | Solidinput, "Built by a 16px favicon." (2026-11-20) | 1080×1080 | pixel-rasterized favicon | chiptune `scripts/score.py` |
| `example-reels/` | Din Firmaadresse, "Your post, handled." (2026-11-21) | 1080×1920 master | vector logo, hook opening | effects only `scripts/score-sfx.py` |
| `example-square/` | the same film cut for X | 1080×1080 | vector logo, hook opening | effects only |

Read `references/method.md` before you write any code: it holds the engine, the layout math, the hook opening, the square cut and every lesson from both runs.

For a requested cinematic ending or a reference-frame correction, read [Cinematic reveals and shot revisions](references/cinematic-reveals.md). A product control can carry the action into an illustrated or photographic scene. Let the requested beats set the duration. For revisions, start from the approved edit and carry its creative decisions forward.

## 1. Intake: interview first

Read the brand source before you ask anything (step 1 of the workflow), so you ask only what the site, repo or `DESIGN.md`/`PRODUCT.md` cannot answer. Then send **one** message with the open questions, numbered, each with your proposed default so the user can answer "yes" or change one line. Do not ask more than this list.

**The product and the story**
1. **What does it do**, in one sentence a customer would say? ("I get my company post scanned and see it in one dashboard.")
2. **Who watches** the post? (founders, developers, local shop owners…) This sets the copy and the language.
3. **The payoff**: the moment a customer feels the value. It becomes the film's big landing ("invoice PAID", "letter scanned", "site live"). Propose one from the product.
4. **What the logo builds**: 3-5 real screens or steps in order (login → mail list → invoice). Propose them from the product's routes or homepage.
5. **One surprise** mid-film that only this product can do (Din Firmaadresse: the scanner scans the logo and it lands in its own mailbox). Propose one.

**What may be on screen**
6. **Names on screen**: which company and which person name to show. Use the user's own company, never the site's demo persona or a real customer. Ask how the owner wants to be named (short name or none). Never use a private email: use a public one (`kontakt@…`) or none.
7. **Facts**: prices, plan names, numbers. Take them from code or the live site; never invent counts, ratings or testimonials. Confirm the legal entity name if it differs from the brand.
8. **Must avoid**: legal claims, competitors, third-party logos, words the brand bans.

**The post**
9. **Hook line** (frame 0) and **end line** (last 2 s): offer two drafts of each. Hook names the joke ("We gave our logo / a job."); end line names the value ("Your post, handled.").
10. **Where it goes**: default is both a 1080×1920 master (Reels, TikTok, Shorts) and a 1080×1080 cut (X, LinkedIn feed). Language of the copy.
11. **Sound**: playful chiptune, a calm soft score (marimba, plucks), or **effects only** (paper, clicks, stamps). Recommend effects only for Reels/TikTok, where the user adds a library track; offer a score for X.

If the user names a hero that belongs to another company (for example Anthropic's Clawd), say that it is not theirs to use and offer their own mark instead.

Then reply with a short **beat sheet** (time → action → what changes on screen → sound) and wait for a yes, unless the user said "no stops".

## 2. Workflow

1. **Context.** Read the brand source. For a site, take a full-page screenshot (`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=1280,2400 --screenshot=<scratch>/site.png <url>`) and a phone-width one (`--window-size=430,932`), and look at both. Note: grounds, accent colour, display and body fonts, signature details (dither, grids, shadows, corners). In a repo, read `DESIGN.md`, `PRODUCT.md`, the logo SVG, the i18n strings for real UI copy and the constants for prices.
2. **Interview.** Section 1. Then the beat sheet.
3. **Project.** In the session scratchpad: `DO_NOT_TRACK=1 npx hyperframes init <name> --skip-skills`. Always prefix HyperFrames commands with `DO_NOT_TRACK=1` (it sends telemetry otherwise). Download the brand fonts as `.woff2` into `assets/fonts/` and GSAP into `assets/lib/` (no CDN at render time). See method.md §Setup.
4. **Default logo-film beat sheet.** 120 BPM, beat = 0.5 s, 14 s = 28 beats. Frame 0 is the thumbnail: open on the **hook frame** (method.md §Hook opening): the hero big (~500-560 px tile, eyes open, legs on) under the bold two-line hook, accent colour on the last words. At ~0.95 s it shrinks into its tab while the browser rises in; at 1.5 s it breaks out. Every hop lands on a beat and changes something; a hop that changes nothing is cut. One surprise mid-film. The payoff lands hard (screen shake, the loudest sound). The hero returns to its tab, then the end line holds ≥ 2 s.
5. **Build the master.** Start from the example closest to the brief, copy its `index.html` and `compositions/film.html`, then replace the brand parts listed in method.md §What to swap. Keep the engine: one paused GSAP tween drives a pure `render(t)`. Rasterize the hero SVG into square cells if the brand is pixel-styled; keep the vector if not.
6. **Check.** `DO_NOT_TRACK=1 npx hyperframes check` (vertical: default safe zones; square: `--safe-zone=standard`). Fix errors. Intended overlaps (debris, falling letters) get `data-layout-allow-overlap`; small browser-chrome text gets `data-layout-ignore`. The hook line stays ≥ 1.27 s; the closing line ≥ 2 s.
7. **Look.** `npx hyperframes snapshot --at <0, 0.75, 1.0, 1.1, 1.2, 1.3, 1.45, every landing + 0.1 s, end> --no-end -o <scratch>/snaps` and read the contact sheet. Fix what you see (hero crossing the hook line, hero lost on a same-colour ground, text off-frame or under platform UI, hero covering copy, two panels visible at once, a name too wide for its box). Use `--zoom "<selector>"` to check tight text. Repeat until clean.
8. **Sound.** Copy `scripts/score.py` (score) or `example-reels/scripts/score-sfx.py` (effects only, `python score-sfx.py out.wav [music_gain]`), set the event times to match `HOPS` and the other times in `film.html`, render the WAV with a venv (`python3 -m venv <scratch>/venv && <scratch>/venv/bin/pip install numpy scipy`, run with `-I`), normalise with `loudnorm` (score `I=-14.5:TP=-1.5:LRA=7`; effects only `I=-18:TP=-1.5:LRA=11`, which leaves room for a library track), and add it to `index.html` as `<audio id="score" class="clip" ...>`. Check per-half-second loudness: quiet intro, the payoff loudest, nothing poking out.
9. **Render.** `DO_NOT_TRACK=1 npx hyperframes render --quality delivery -o <scratch>/<name>.mp4`. Verify with `ffprobe` (duration = root `data-duration`, h264 + aac) and a frame sheet from the MP4 (`ffmpeg -vf "select='not(mod(n\,26))',scale=270:480,tile=8x2"`). Run `npx hyperframes audio <mp4> --json` and confirm onsets match landings. Export frame 0 as `thumbnail.png`.
10. **Square cut.** Copy the project to `<name>-x`, apply method.md §Square cut (about ten constants), check with `--safe-zone=standard`, snapshot, render `<name>-x.mp4` and `thumbnail-x.png`.
11. **Deliver.** Copy both MP4s, both thumbnails and both projects to `~/Movies/<name>/` (the scratchpad is temporary). Report: paths, size, length, formats, what was checked, and that the sound was measured, not heard.
12. **Post.** Write `post.md` next to the films: the Reels caption and the X thread from `references/x-thread.md`. Offer a "making of" video only as a follow-up.

Feedback rounds are normal (the Din Firmaadresse film took five: names, music, hook, a short name, the square cut). Change the source, re-check, re-snapshot the changed moments, re-render; keep the previous MP4 under a `-v1-…` name only when the change is a matter of taste (music).

## 3. Rules that matter

- The film shows the user's real brand: real copy, real product names, real prices. Draw only what has no source.
- No demo personas, no real customers' names, no private emails or personal data on screen. Ask how people want to be named.
- Keep the brand's own type and colour rules (Solidinput: pixel face for headings only, orange as a whole field or single squares; Din Firmaadresse: one amber "seal" per view).
- The hero must read on every ground it crosses. If it shares the accent colour, give it an outline after the joke (method.md §Hero).
- Hops back to back need a 0.1 s gap between landing and the next take-off, or the squash and the crouch fight.
- Vertical: keep text and the action out of the top ~14 % and bottom ~35 % (Reels, TikTok and Shorts UI). Square for X: nothing is covered.
- A page change is a cut (≤ 0.08 s), never a slow crossfade: two readable panels at once look broken.
- Never post or upload anything. Hand the user the files and the text.

## 4. Credits

The idea of a character building a real interface as code, with synthesized sound on one timeline, comes from the Clawd Motion Lab "No After Effects" prompt (Clawd building a motion graphic in an After Effects-style UI, Blender + HTML). This skill keeps it 2D, swaps the mascot for the brand's own logo, and adds the hook opening, the interview, the vertical and square cuts and the checks. Rendering is HyperFrames by HeyGen (Apache-2.0); animation is GSAP.
