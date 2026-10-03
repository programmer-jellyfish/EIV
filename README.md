# E-Ink & Evidence
*Every page hides a clue.* 500 deterministic murder cases, server-rendered for the **Kobo Clara** browser.

## Architecture
Flask returns tiny HTML pages. No JavaScript at all, no SPA, no external requests, no images, no web fonts. Navigation is plain `<a>` links; the case-number box is a plain GET form; RANDOM CASE is a server-side redirect.

URLs: `/`, `/open?n=`, `/random`, `/case/N`, `/case/N/{briefing,scene,scene2,suspects,s1..s5,timeline,evidence,evidence2,accuse,result,menu}`, `/case/N/accuse/I[/K]`, `/archive/P`.
Every page has PREVIOUS / MENU / NEXT links (large tap targets, black-on-white, works in grayscale). Content is split into short pages so scrolling should rarely be needed.

## Run
    pip install -r requirements.txt
    python app.py          # then open http://<your-computer-ip>:5000 on the Kobo
Deploy: `pip install gunicorn && gunicorn -b 0.0.0.0:8000 app:app` behind any reverse proxy. The Kobo must reach the server over Wi-Fi (same network or public host).

## Case generation
`build(n)` seeds `random.Random(n*7919+13)`, so case N is always identical. Each case has a trace at the scene shared by exactly two suspects (culprit and decoy). Alibi checks break for two suspects (culprit and a red herring hiding a secret). Only the culprit has **both**, and also names the undisclosed weapon. The solution page spells out this logic. Other red herrings: a settled quarrel and an unrelated burned letter. Endings: wrong accusation (with why that suspect fails), solved, and "perfect deduction".

## APIs / offline
No external APIs are used. Everything works offline once the server is reachable.

## Limitations
- Not tested on a physical Kobo; the HTML/CSS is deliberately conservative but a real-device check is advisable. Page length depends on device font settings.
- Cases share templates; variety comes from combination, not hand-written prose.
- Needs a server (Flask); the Kobo cannot run it.

## Extending
Edit the pools at the top of `app.py` (`LOCS`, `TRAITS`, `MOT`, `AL`, `REL`, ...). Add pages by extending `page()` and `ORDER`. Changing pools changes which case each number produces. Optional APIs (e.g. Open Library flavour text) should only ever be additive.
