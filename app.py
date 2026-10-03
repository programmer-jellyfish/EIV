"""E-Ink & Evidence - server-rendered murder mysteries for the Kobo Clara browser.
No JavaScript anywhere. Every page is a real URL. Case N is always the same case."""
import random
from functools import lru_cache
from flask import Flask, redirect, abort, request

app = Flask(__name__)
FIRST = "Edith Arthur Clara Hugo Vera Julian Mabel Oswald Iris Felix Nora Silas Ada Leopold Rosa Victor Tilda Cedric Lena Marlow Ivy Rupert Opal Gideon Hazel Beatrice Edmund Florence Ambrose Celia Percival Agnes Lionel Margot Tobias Lavinia Ernest Daphne Basil Cora Wilfred Elspeth Malcolm Sybil Alistair Josephine Augustus Minerva Conrad Imogen Barnaby Frances Octavia Miles Rosalind Edwin Prudence Simon Theodora Giles Harriet Lucian Phoebe Stanley Miriam Anselm Winifred".split()
LAST = "Ashby Blackwood Crane Delaney Ellery Fenwick Gray Holloway Ingram Jarvis Kemp Lockhart Mercer Nash Pryce Quill Rook Sterling Thorne Voss Wren Yardley Hale Finch Marsh Bellamy Calder Dacre Easton Fairchild Gresham Hargreaves Isley Jermyn Kingsley Loxley Mordaunt Nightingale Ormond Pemberton Rivington Sutherland Trelawney Underwood Vale Westcott Yarrow Bexley Canning Drummond Eversleigh Frobisher Greaves Harcourt Ives Jolliffe Ketteridge Latham Mowbray Northcott Penrose Radcliffe Sorrell Tewkesbury Umberleigh Vane Whitcombe Yorke".split()
# place, room, weapons "weapon|cause"
LOCS = [
 ("the manor", "the study", "a brass candlestick|blunt force trauma", "a fireplace poker|blunt force trauma"),
 ("the hotel", "Room 12", "a silk scarf|strangulation", "a champagne bottle|blunt force trauma"),
 ("the library", "the rare-books room", "a marble bookend|blunt force trauma", "a paper knife|a stab wound"),
 ("the theatre", "the prop room", "a stage dagger|a stab wound", "a sandbag rope|strangulation"),
 ("the university", "the dean's office", "a bronze bust|blunt force trauma", "a poisoned sherry|poisoning"),
 ("the museum", "the Egyptian gallery", "an antique mace|blunt force trauma", "a curator's spike|a stab wound"),
 ("the night train", "the dining car", "a carving knife|a stab wound", "a tea laced with arsenic|poisoning"),
 ("the restaurant", "the wine cellar", "a corkscrew|a stab wound", "a poisoned port|poisoning"),
 ("the law firm", "the private office", "a heavy ledger|blunt force trauma", "a letter opener|a stab wound"),
 ("the bookstore", "the back stockroom", "a ladder rung|blunt force trauma", "a bookbinder's awl|a stab wound"),
 ("the gallery", "the framing room", "a picture-frame hammer|blunt force trauma", "a length of wire|strangulation"),
 ("the laboratory", "the cold store", "a poisoned flask|poisoning", "a steel tripod|blunt force trauma"),
 ("the apartment", "the sitting room", "a cast-iron doorstop|blunt force trauma", "a dressing-gown cord|strangulation"),
 ("the garden house", "the glasshouse", "a garden trowel|a stab wound", "a flowerpot|blunt force trauma"),
 ("the warehouse", "the loading office", "a crowbar|blunt force trauma", "a hook chain|strangulation"),
 ("the ocean liner", "the wireless room", "a signal wrench|blunt force trauma", "a length of piano wire|strangulation"),
 ("the country club", "the billiards room", "a cue butt|blunt force trauma", "a poisoned brandy|poisoning"),
 ("the observatory", "the dome chamber", "a brass telescope|blunt force trauma", "a snapped guy wire|strangulation"),
 ("the radio station", "the sound booth", "a microphone stand|blunt force trauma", "a glass recording stylus|a stab wound"),
 ("the botanical gardens", "the orchid house", "a pruning knife|a stab wound", "a toxic tincture|poisoning"),
 ("the auction house", "the cataloguing room", "a gavel|blunt force trauma", "a letter knife|a stab wound"),
 ("the seaside pavilion", "the locked bandstand", "a cornet mute|blunt force trauma", "a silk sash|strangulation"),
 ("the city baths", "the Turkish bath", "a marble soap dish|blunt force trauma", "a poisoned tonic|poisoning"),
 ("the private museum", "the map room", "a stone paperweight|blunt force trauma", "a compass divider|a stab wound"),
 ("the courthouse", "the records vault", "a bronze desk seal|blunt force trauma", "a sharpened quill|a stab wound"),
 ("the mountain lodge", "the drying room", "an ice axe|blunt force trauma", "a climbing rope|strangulation"),
 ("the conservatory", "the potting shed", "a pruning saw|a stab wound", "a sack of soil|suffocation"),
 ("the film studio", "the editing suite", "a camera tripod|blunt force trauma", "a strip of film leader|strangulation"),
 ("the embassy", "the cipher office", "a bronze letter weight|blunt force trauma", "a poisoned cordial|poisoning"),
 ("the market hall", "the flower arcade", "a florist's shears|a stab wound", "a fallen marble urn|blunt force trauma"),
 ("the clockmaker's workshop", "the escapement room", "a steel mainspring|strangulation", "a brass caliper|blunt force trauma"),
 ("the motor club", "the trophy room", "a silver cup|blunt force trauma", "a tire iron|blunt force trauma"),
 ("the country rectory", "the vestry", "a brass censer|blunt force trauma", "a poisoned communion wine|poisoning"),
 ("the printworks", "the composing room", "a type-metal slug|blunt force trauma", "a bookbinder's knife|a stab wound")]
ADJ = "Silent Crimson Hollow Midnight Gilded Broken Quiet Last Ashen Velvet Hidden Bitter Paper Fading Locked Crooked Distant Tarnished Winter Riven Secret Waning Blue Unquiet Glass".split()
TITLE_NOUNS = "Witness Cipher Inheritance Portrait Alibi Testament Locket Telegram Clockwork Deception Encore Ledger Secret Dispatch Masquerade Footprint Silence Emerald Scandal Promise Passenger Keepsake Phantom Manuscript Riddle Heiress Counterfeit Conspiracy Overture Keyhole Bloodline Blackmail Verdict Memory Debt Expedition Alias Invitation Betrayal Forgery Gambit Horizon Shadow Finale Waltz Astrolabe Brooch Casket Decanter Epilogue Folio Garnet Heirloom Impostor Jubilee Labyrinth Medallion Obituary Paradox Reliquary Sonnet Talisman Undertow Vengeance Whisper".split()
PROF = "retired judge,antiques dealer,newspaper editor,opera singer,chemist,librarian,banker,architect,hotelier,critic,professor,tailor,collector,physician,publisher,cartographer,stage magician,ship's purser,botanist,horologist,concert pianist,restaurateur,archivist,portrait painter,astronomer,foreign correspondent,industrialist,auctioneer,radio dramatist,magistrate,ornithologist,novelist,violin maker,geologist,interior decorator".split(",")
REL = "business partner,estranged sibling,personal secretary,former apprentice,professional rival,old friend,landlord,family physician,named heir,creditor,neighbour,cousin,investor,ex-fiance,travel companion,legal counsel,wartime comrade,housekeeper,tenant,patron,editor,former student,co-author,stepchild,ward,club associate,shipping agent,disinherited niece,debtor,confidant".split(",")
MOT = ["stood to inherit", "was owed a large debt", "was about to be exposed", "had been passed over for promotion",
    "was jilted by the victim", "feared being dismissed", "had a decades-old grudge", "was cut out of a contract",
    "believed the victim had stolen their research", "was being blackmailed over a forged signature", "wanted a rare collection sold before dawn",
    "feared an old identity would be revealed", "had secretly diverted the company's wages", "was protecting a family scandal",
    "thought the victim had sabotaged a marriage", "was about to lose a patent", "resented a humiliating public review",
    "needed the victim's vote on a disputed will", "had sold a counterfeit as the original", "was hiding a missing ledger",
    "believed the victim caused a sibling's disgrace", "wanted to stop a dangerous expedition", "was being forced to repay a ruinous loan",
    "feared their anonymous letters would be traced", "had secretly sold the theatre's future rights", "was protecting a smuggling route",
    "thought the victim planned to close the hospital wing", "was desperate to recover a stolen inheritance", "had been accused of fixing a race",
    "wanted to keep a failed investment secret", "was furious over a changed testament", "feared a long-lost child would be named heir"]
AL = [("in the cloakroom", "the cloakroom ticket"), ("at the bar", "the bar tab"), ("on the telephone", "the exchange log"),
      ("in the kitchen", "the cook's night book"), ("at the front desk", "the signing-in ledger"),
      ("in the garden", "the gardener's lamp log"), ("in the card room", "the card-room scoresheet"),
    ("in the parlour", "the maid's rota"), ("at the station kiosk", "the porter's parcel book"),
    ("in the reading room", "the attendance register"), ("at the river landing", "the ferryman's tally"),
    ("in the projection booth", "the reel-change log"), ("at the infirmary", "the night nurse's chart"),
    ("in the billiards room", "the marker's chalk board"), ("at the switchboard", "the operator's call sheet"),
    ("in the chapel", "the verger's candle record"), ("on the roof walk", "the watchman's patrol book"),
    ("in the map room", "the signed-out chart ledger"), ("at the pastry counter", "the baker's delivery slate"),
    ("in the garage", "the mechanic's work docket"), ("at the ticket window", "the cashier's stub roll"),
    ("in the music room", "the accompanist's rehearsal notes"), ("by the greenhouse", "the head gardener's watering chart"),
    ("at the customs desk", "the inspector's seal register"), ("in the press room", "the printer's job ledger")]
TRAITS = [("a smear of blue chalk", "dusts their cuffs with blue chalk"), ("a scent of violet pomade", "wears violet pomade"),
          ("a bent brass button", "is missing a brass coat button"), ("a pressed lily petal", "wears a lily in the lapel"),
          ("grey cat hairs", "keeps a grey cat"), ("a drop of green ink", "writes only in green ink"),
                    ("flecks of red sealing wax", "seals letters with red wax"), ("a pearl bead", "has a broken pearl necklace"),
                    ("a thread of gold embroidery", "wears a gold-embroidered waistcoat"), ("a streak of printer's ink", "sets type by hand"),
                    ("a trace of lavender soap", "uses lavender soap"), ("a sliver of black lacquer", "carries a lacquered cane"),
                    ("a grain of pale sand", "keeps a jar of beach sand"), ("a fleck of silver polish", "polishes antique silver"),
                    ("a feather of grey down", "wears a down-lined overcoat"), ("a curl of copper wire", "repairs electrical instruments"),
                    ("a smear of stage rouge", "works backstage at the theatre"), ("a trace of beeswax", "makes candles as a hobby"),
                    ("a scrap of blue silk", "owns a blue silk scarf"), ("a spot of black grease", "works on motorcars"),
                    ("a pinch of dried fennel", "keeps a kitchen herb box"), ("a grain of red sand", "collects geological specimens"),
                    ("a fleck of white paint", "restores picture frames"), ("a trace of camphor", "stores mothballs in their wardrobe")]
OTHER = ["is always punctual", "hums when nervous", "is left-handed", "takes snuff", "wears spectacles", "is very tall",
                 "quotes poetry at awkward moments", "keeps a pocket watch five minutes fast", "cannot bear aniseed", "collects hotel keys",
                 "speaks in a whisper", "has a remarkable memory for faces", "is learning to play the mandolin", "never removes their gloves",
                 "is an insomniac", "has a limp from an old riding accident", "folds every newspaper into quarters", "is always cold",
                 "uses a fountain pen with purple ink", "can identify ships by their whistle"]
SCN = ["A lamp lies overturned and one chair is pushed back.", "A teacup is cold and half full; the clock has stopped.",
       "Papers are scattered, but the strongbox is untouched.", "The window is latched from inside; the door was not forced.",
             "A coat hangs on the door and the fire has burned low.", "A phonograph needle rests in a silent groove; the record is still turning.",
             "Rain beads on the sill, though the carpet beneath the window is dry.", "A chair faces the wall; a second glass bears a lipstick mark.",
             "The room smells of lamp oil, but every wick is neatly trimmed.", "A pocket watch lies open at the wrong time; its hands still move.",
             "A draft has lifted one corner of a map; a paperweight is missing.", "The hearth is cold, yet a single glove is warm to the touch.",
             "A music box has stopped mid-tune; its key is wound tight.", "A wet footprint ends in the middle of the rug.",
             "The desk is locked, but a fresh scratch crosses the brass keyhole.", "A vase has been turned toward the wall; its water is cloudy.",
             "A telegram lies unopened beneath a glass of water.", "The room is tidy except for one muddy wheel track.",
             "A candle has guttered out beside a clean, untouched matchbook.", "A window stands open against the rain; the curtains are perfectly dry."]
SECRETS = ["...meet me in secret, as before...", "...the second ledger is beneath the west stair...", "...do not send the original to Bellamy...",
                     "...the names on the passenger list were altered...", "...I can prove the portrait is a copy...", "...the north gate will be unlatched at midnight...",
                     "...burn the draft after you have read it...", "...the shipment never reached the island...", "...your brother's letter was intercepted...",
                     "...the clock was already stopped when I arrived...", "...I will return the missing page before the vote...", "...the child must not learn who paid for it..."]
QUARRELS = ["a disputed bill", "a public insult at the club", "the sale of a family portrait", "a missing page from the company ledger",
                        "an accusation of plagiarism", "a broken engagement", "the ownership of a racehorse", "a contract signed under pressure",
                        "the cancellation of a concert", "a boundary wall on the country estate", "a humiliating review", "a loan that had already been repaid",
                        "the restoration of a forged painting", "a seat on the hospital board", "a letter opened without permission", "the transfer of an old title"]

def t(m): return "%d:%02d pm" % (m // 60 % 12 or 12, m % 60)

@lru_cache(maxsize=600)
def build(n):
    r = random.Random(n * 7919 + 13)
    pl, room, *ws = r.choice(LOCS); w, cause = r.choice(ws).split("|")
    nm = [a + " " + b for a, b in zip(r.sample(FIRST, 6), r.sample(LAST, 6))]
    c = r.randrange(5)
    decoy = r.choice([i for i in range(5) if i != c])
    rest = [i for i in range(5) if i not in (c, decoy)]
    r.shuffle(rest); rh1, rh2, plain = rest
    trace, trait = r.choice(TRAITS)
    d = dict(n=n, pl=pl, room=room, w=w, cause=cause, vic=nm[0], s=nm[1:], c=c, decoy=decoy, rh1=rh1, rh2=rh2, plain=plain,
             prof=r.choice(PROF), trace=trace, trait=trait, T=1140 + 5 * r.randrange(36), scn=r.choice(SCN),
             secret=r.choice(SECRETS), quarrel=r.choice(QUARRELS),
             rel=r.sample(REL, 5), mot=r.sample(MOT, 5), al=r.sample(AL, 5), oth=r.sample(OTHER, 5))
    d["title"] = "The %s %s" % (r.choice(ADJ), r.choice(TITLE_NOUNS))
    return d

def broken(d):
    # Several people have rough alibis, but only the killer fits the full pattern.
    return {d["c"], d["decoy"], d["rh1"], d["rh2"]}

def suspect_page(d, i):
    T, w, vic = d["T"], d["w"], d["vic"]
    c = i == d["c"]; al = d["al"][i]
    if i in broken(d): stay = "from %s until well after %s" % (t(T - 45), t(T + 20))
    else: stay = "from %s to %s" % (t(T - 40), t(T + 30))
    trait = d["trait"] if i in (d["c"], d["decoy"], d["rh1"]) else d["oth"][i]
    beh = {d["c"]: "measured, deliberate, and notably calm under pressure.", d["decoy"]: "too polished, almost rehearsed, and quick to deny any familiarity.",
           d["rh1"]: "irritated, sharp-tongued, and trying not to say too much.", d["rh2"]: "restless, glancing at the door and fidgeting with something in their pocket.",
           d["plain"]: "quiet and polite, but given to long pauses before answering."}[i]
    say = ('"I had no reason to touch %s. I was trying to keep the peace."' % vic) if c else (
        '"I saw someone else in the room, but I cannot say who."' if i in (d["decoy"], d["rh1"]) else '"I do not know what happened."')
    return ("<p><b>%s</b><br>%s</p><p>Motive: %s.</p><p>Alibi: \"I was %s %s. Check %s.\"</p>"
            "<p>Notes: %s %s.</p><p>Said to police: %s</p>"
            % (d["s"][i], d["rel"][i].capitalize() + " of the victim", d["mot"][i], al[0], stay, al[1], beh.capitalize(),
               trait, say))

def page(d, slug):
    T, S, vic = d["T"], d["s"], d["vic"]
    if slug == "":
        return "Case %d" % d["n"], "<h2>%s</h2><p>%s, %s, is dead at %s.</p><p>Five suspects. One killer. Every page hides a clue.</p>" % (d["title"], vic, d["prof"], d["pl"])
    if slug == "briefing":
        return "Briefing", ("<p><b>%s</b>, %s, was found dead in %s at %s, at %s.</p><p>Died about: %s<br>Cause: %s<br>Weapon: %s</p>"
                            "<p><i>The weapon has not been disclosed to anyone in the household.</i></p>" % (vic, d["prof"], d["room"], d["pl"], t(T + 25), t(T), d["cause"], d["w"]))
    if slug == "scene": return "Crime Scene", "<p>%s</p><p>Nothing was forced. The killer was let in, or was already there.</p>" % d["scn"]
    if slug == "scene2":
        return "Scene: Details", "<p>Beside the body: <b>%s</b>.</p><p>It is not a unique trace, only a useful one: several people work with similar materials, but the placement suggests the killer was close enough to leave it behind without appearing to set it there deliberately.</p>" % (d["trace"])
    if slug == "suspects":
        return "Suspects", "<ul>%s</ul>" % "".join('<li><a class="b" href="/case/%d/s%d">%d. %s</a> (%s)</li>' % (d["n"], i + 1, i + 1, S[i], d["rel"][i]) for i in range(5))
    if slug[0] == "s" and slug[1:].isdigit() and 1 <= int(slug[1:]) <= 5:
        return "Suspect %s" % slug[1:], suspect_page(d, int(slug[1:]) - 1)
    if slug == "timeline":
        return "Timeline", ("<p>%s - %s and %s quarrel over %s.<br>%s - Smoke from the grate: %s burns a letter.<br>%s - Guests scatter to separate rooms.<br>"
                    "<b>%s - %s dies.</b><br>%s - Body found.<br>%s - Police arrive.</p>" % (t(T - 100), S[d["rh1"]], vic, d["quarrel"], t(T - 35), S[d["rh2"]], t(T - 60), t(T), vic, t(T + 25), t(T + 40)))
    if slug == "evidence":
        rows = "".join("<li>%s: %s - %s</li>" % (S[i], d["al"][i][1], "CONFLICT, shows departure at %s" % t(T - 15) if i in broken(d) else "consistent") for i in range(5))
        return "Evidence", "<p><b>A.</b> Trace at scene: %s.</p><p><b>B.</b> Alibi checks:</p><ul>%s</ul>" % (d["trace"], rows)
    if slug == "evidence2":
        return "Evidence: Notes", ("<p><b>C.</b> Ash fragment from the grate: \"%s\"</p><p><b>D.</b> The quarrel concerned %s; it matters less than the timing and who was alone with the victim.</p><p><b>E.</b> Nobody was told the weapon used. Listen for the person who mentions the wrong method, or the right one too confidently.</p>" % (d["secret"], d["quarrel"]))
    if slug == "accuse":
        return "Accusation", "<p>Who killed %s?</p><ul>%s</ul>" % (vic, "".join('<li><a class="b" href="/case/%d/accuse/%d">%d. %s</a></li>' % (d["n"], i + 1, i + 1, S[i]) for i in range(5)))
    if slug == "result": return "Case Result", '<p>No accusation yet.</p><p><a class="b" href="/case/%d/accuse">MAKE ACCUSATION</a></p>' % d["n"]
    if slug == "menu":
        items = [("briefing", "CASE BRIEFING"), ("scene", "CRIME SCENE"), ("suspects", "SUSPECTS"), ("timeline", "TIMELINE"), ("evidence", "EVIDENCE"),
                 ("accuse", "MAKE ACCUSATION"), ("result", "CASE RESULT")]
        return "Menu", "<ul>%s<li><a class=\"b\" href=\"/archive/1\">CASE ARCHIVE</a></li><li><a class=\"b\" href=\"/\">HOME</a></li></ul>" % "".join('<li><a class="b" href="/case/%d/%s">%s</a></li>' % (d["n"], s, l) for s, l in items)
    return None

ORDER = ["", "briefing", "scene", "scene2", "suspects", "s1", "s2", "s3", "s4", "s5", "timeline", "evidence", "evidence2", "accuse", "result"]

CSS = ("body{font-family:Georgia,'Times New Roman',serif;font-size:20px;line-height:1.35;color:#000;background:#fff;margin:0;padding:8px 14px}"
       "h1{font-size:15px;letter-spacing:2px;margin:0;padding:4px 0;border-bottom:3px double #000}h2{font-size:24px;margin:8px 0}p{margin:8px 0}"
       "ul{margin:6px 0;padding-left:0;list-style:none}li{margin:8px 0}a{color:#000}.b{display:block;border:2px solid #000;padding:10px;text-decoration:none;font-weight:bold}"
       "table{width:100%;border-collapse:separate;border-spacing:4px;margin-top:10px}td{width:33%;padding:0}td a{display:block;border:2px solid #000;padding:14px 2px;text-align:center;text-decoration:none;font-weight:bold;font-size:17px}"
       "input{font-size:22px;padding:8px;width:35%}.s{font-size:22px;font-weight:bold;padding:10px;border:2px solid #000;background:#fff}")

def html(h1, body, prev=None, nxt=None, menu=None):
    nav = ""
    if menu:
        cell = lambda u, l: "<td>%s</td>" % ('<a href="%s">%s</a>' % (u, l) if u else "")
        nav = "<hr><table><tr>%s%s%s</tr></table>" % (cell(prev, "&#9664; PREVIOUS"), cell(menu, "&#9776; MENU"), cell(nxt, "NEXT &#9654;"))
    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>E-Ink &amp; Evidence</title>'
            '<style>%s</style></head><body><h1>E-INK &amp; EVIDENCE</h1><h2>%s</h2>%s%s</body></html>' % (CSS, h1, body, nav))

@app.route("/")
def home():
    msg = '<p style="color:#000"><b>Enter a number from 1 to 500.</b></p>' if request.args.get("e") else ""
    return html("Every page hides a clue.", msg + '<hr><p>ENTER CASE NUMBER</p><form action="/open" method="get"><input type="text" name="n" size="4" maxlength="3"> '
                '<input class="s" type="submit" value="OPEN CASE"></form><p>1 - 500</p><hr><a class="b" href="/random">RANDOM CASE</a>'
                '<p><a href="/archive/1">Case archive</a></p>')

@app.route("/open")
def open_case():
    try: n = int(request.args.get("n", "").strip())
    except ValueError: n = 0
    return redirect("/case/%d" % n if 1 <= n <= 500 else "/?e=1")

@app.route("/random")
def rnd(): return redirect("/case/%d" % random.randint(1, 500))

@app.route("/archive/<int:p>")
def archive(p):
    if not 1 <= p <= 50: abort(404)
    rows = "".join('<li><a href="/case/%d">%d. %s</a></li>' % (k, k, build(k)["title"]) for k in range((p - 1) * 10 + 1, p * 10 + 1))
    return html("Archive %d/50" % p, "<ul>%s</ul>" % rows, "/archive/%d" % (p - 1) if p > 1 else "/", "/archive/%d" % (p + 1) if p < 50 else None, "/")

def guard(n):
    if not 1 <= n <= 500: abort(404)
    return build(n)

@app.route("/case/<int:n>")
def cover(n): return show(n, "")

@app.route("/case/<int:n>/<slug>")
def show(n, slug):
    d = guard(n)
    if slug == "scene2" or slug in ORDER or slug == "menu":
        res = page(d, slug)
        if res:
            hd = "Case %d: %s" % (n, res[0]) if slug else res[0]
            base = "/case/%d/" % n
            if slug == "menu": return html("Menu", res[1], base + "briefing", None, base)
            i = ORDER.index(slug)
            prev = base + ORDER[i - 1] if i else "/"
            nxt = base + ORDER[i + 1] if i < len(ORDER) - 1 else base + "menu"
            return html(hd, res[1], prev, nxt, base + "menu")
    abort(404)

@app.route("/case/<int:n>/accuse/<int:i>")
@app.route("/case/<int:n>/accuse/<int:i>/<k>")
def accuse(n, i, k=None):
    d = guard(n)
    if not 1 <= i <= 5: abort(404)
    i -= 1; S = d["s"]; c = d["c"]; base = "/case/%d" % n; menu = base + "/menu"
    if i != c:
        why = {d["decoy"]: "The pattern fits their panic, but not the room's timing or the final note.",
               d["rh1"]: "There was a quarrel, but it was old and settled; it does not explain the murder window.",
               d["rh2"]: "Their alibi breaks, yet they still lack the combination of proximity, motive, and a useful secret.",
               d["plain"]: "This theory ignores the physical trace and the killer's knowledge of the victim's habits."}[i]
        return html("WRONG ACCUSATION", "<p>That does not fit the full record. %s</p><p>Check the pattern, not the loudest motive.</p>" % why,
                    base + "/accuse", "/", menu)
    if k is None:
        rot = n % 3; opts = [("1", "The alibi record conflict"), ("2", "The strongest motive"), ("3", "The trace alone")]
        opts = opts[rot:] + opts[:rot]
        return html("CASE SOLVED", "<p>%s is the killer. One more question: what separates them from the other suspect with the same general material trace?</p><ul>%s</ul>" %
                    (S[c], "".join('<li><a class="b" href="%s/accuse/%d/%s">%s</a></li>' % (base, i + 1, kk, l) for kk, l in opts)), base + "/accuse", None, menu)
    head = "PERFECT DEDUCTION" if k == "1" else "CASE SOLVED"
    extra = "You found the decisive link: the killer was the only person who both knew the victim's habits and had a credible reason to be in the room while their alibi collapsed." if k == "1" else "The combination of timing, proximity, and motive was decisive."
    return html(head, "<p>%s</p>%s" % (extra, solution(d)), base + "/accuse", "/random", menu)

def solution(d):
    S = d["s"]; c = d["c"]
    return ("<p>The decisive pattern is the combination of timing, motive, and trace. %s is the only suspect whose motive matches the victim's recent tensions, whose alibi collapses at the critical window, and whose note matches the scene trace. %s may share the same general material trace, but that alone does not explain the sequence of events.</p>" % (S[c], S[d["decoy"]]))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
