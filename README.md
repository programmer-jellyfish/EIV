# E-Ink & Evidence

*Every page hides a clue.*

**E-Ink & Evidence** is a browser-based murder mystery game designed specifically for **e-readers with web browsers**.

It contains **500 deterministic murder cases**, each generated from a case number. Read the briefing, inspect the scene, question suspects, check alibis, examine evidence, and make your accusation. Every page contains another piece of the puzzle.

## Why an E-Reader-Specific Website?

Most websites are designed for phones and computers. E-readers are a very different environment.

E-ink displays are excellent for reading, but they are not designed for the constantly changing, animated interfaces common on the modern web. Many e-readers also have limited processing power, slower browsers, and browsers intended primarily for simple reading and web access.

This means a typical JavaScript-heavy website can be a poor experience on an e-reader.

**E-Ink & Evidence avoids that problem entirely.**

- **No JavaScript**
- **No animations**
- **No external requests**
- **No images**
- **No web fonts**
- **No SPA or client-side rendering**
- **No heavy frameworks**
- **No unnecessary visual effects**

The server generates small HTML pages, and the e-reader simply loads them.

Navigation uses ordinary `<a>` links and the case-number input is a plain GET form. Even **RANDOM CASE** is handled by the server with a redirect.

The result is a website that behaves more like a lightweight digital book than a conventional web application.

## How It Looks

The interface is intentionally **minimal, monochrome, and reader-friendly**.

Everything is built around the limitations and strengths of an e-ink screen:

- Black text on a white background
- Large, clearly separated links
- High contrast
- Large tap targets
- Minimal scrolling
- Short pages instead of dense screens
- No colour-dependent information
- No images that need to load or render
- No animations or transitions

The design works naturally in grayscale, making it suitable for devices ranging from small e-readers to larger e-ink tablets.

Each part of a case is divided into its own short page, so you can progress through the investigation one screen at a time.

The experience is deliberately quiet: **read, investigate, choose, repeat.**

## Architecture

Flask returns tiny server-rendered HTML pages.

There is **no JavaScript at all**. The browser only needs to request a page and display HTML/CSS.

Navigation is handled with ordinary links, while the case-number box uses a plain GET form. `RANDOM CASE` performs a server-side redirect.

### URLs

```text
/
 /open?n=
 /random
 /case/N
 /case/N/briefing
 /case/N/scene
 /case/N/scene2
 /case/N/suspects
 /case/N/s1
 /case/N/s2
 /case/N/s3
 /case/N/s4
 /case/N/s5
 /case/N/timeline
 /case/N/evidence
 /case/N/evidence2
 /case/N/accuse
 /case/N/result
 /case/N/menu
 /case/N/accuse/I[/K]
 /archive/P
```

Every investigation page provides **PREVIOUS / MENU / NEXT** navigation.

## Running It

The e-reader does not run the Flask application itself. A computer, server, or other device runs the application and the e-reader connects to it through its browser.

### 1. Install the requirements

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python app.py
```

The server will be available on port `5000`.

### 3. Open it on your e-reader

Find the computer's local IP address and open:

```text
http://<your-computer-ip>:5000
```

in the e-reader's browser.

The e-reader and computer need to be reachable from each other, usually by being connected to the **same Wi-Fi network**.

### Deployment

For a persistent deployment:

```bash
pip install gunicorn
gunicorn -b 0.0.0.0:8000 app:app
```

It can then be placed behind a reverse proxy or hosted on a server accessible to the e-reader.

## Case Generation

Cases are generated deterministically.

```python
random.Random(n * 7919 + 13)
```

is used as the seed for case `N`.

This means **case 42 will always be case 42**. The same number produces the same investigation every time.

Each case contains:

- A crime scene
- Five suspects
- A shared physical trace
- Alibi information
- Evidence
- A hidden weapon
- Red herrings
- Multiple possible accusation outcomes

The core deduction is deliberately structured.

The trace at the scene is shared by exactly **two suspects**: the culprit and a decoy.

The alibi evidence breaks for exactly **two suspects**: the culprit and a red herring who is hiding a secret.

Only the culprit satisfies **both conditions** and also identifies the undisclosed weapon.

The solution page explains this reasoning rather than simply revealing the answer.

Other distractions include a settled quarrel and an unrelated burned letter.

## Endings

Your investigation can result in:

- **Wrong accusation**: you accuse an innocent suspect, with an explanation of why their evidence does not fit.
- **Solved**: you identify the culprit correctly.
- **Perfect deduction**: you correctly identify the culprit and satisfy the additional deduction requirements.

## Offline Operation

No external APIs are used.

Once the Flask server is running, the game itself requires **no internet connection**. The e-reader only needs network access to the machine running the server.

There are:

- No external APIs
- No analytics
- No external assets
- No external fonts
- No external images

Everything required by the game is generated locally.

## Extending the Game

The main content pools are located near the top of `app.py`.

You can modify pools such as:

```text
LOCS
TRAITS
MOT
AL
REL
```

and other case-generation data to introduce new combinations.

Additional investigation pages can be added through `page()` and `ORDER`.

Because cases are generated from deterministic seeds, **changing the content pools can change the case produced by an existing case number**.

Optional APIs can be added later, but they should remain purely additive. The core game should continue to work without them.

## Limitations

- The game has not been tested on every physical e-reader. The HTML/CSS is deliberately conservative, but real-device testing is recommended.
- Different e-readers and font settings can change how much content fits on a page.
- Cases use shared templates. Variety comes primarily from combinations of generated locations, suspects, motives, relationships, evidence, and other elements rather than individually written cases.
- The e-reader requires a browser capable of loading the server-rendered HTML.
- A Flask server must run somewhere. The e-reader itself does not run the application.

## The Goal

E-Ink & Evidence is built around a simple idea:

**An e-reader doesn't need to behave like a phone to be useful on the web.**

Instead of forcing a modern web application onto an e-ink device, the game works with the device's limitations.

No JavaScript.  
No loading circus.  
No visual clutter.

Just a murder, a few suspects, a trail of evidence, and one very suspicious little screen.
