"""E-Ink & Evidence - server-rendered murder mysteries for the Kobo Clara browser.
No JavaScript anywhere. Every page is a real URL. Case N is always the same case."""
import random
from functools import lru_cache
from flask import Flask, redirect, abort, request

app = Flask(__name__)
FIRST = "Edith Arthur Clara Hugo Vera Julian Mabel Oswald Iris Felix Nora Silas Ada Leopold Rosa Victor Tilda Cedric Lena Marlow Ivy Rupert Opal Gideon Hazel".split()
LAST = "Ashby Blackwood Crane Delaney Ellery Fenwick Gray Holloway Ingram Jarvis Kemp Lockhart Mercer Nash Pryce Quill Rook Sterling Thorne Voss Wren Yardley Hale Finch Marsh".split()
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
 ("the warehouse", "the loading office", "a crowbar|blunt force trauma", "a hook chain|strangulation")]
ADJ = "Silent Crimson Hollow Midnight Gilded Broken Quiet Last Ashen Velvet Hidden Bitter Paper Fading Locked".split()
PROF = "retired judge,antiques dealer,newspaper editor,opera singer,chemist,librarian,banker,architect,hotelier,critic,professor,tailor,collector,physician,publisher".split(",")
REL = "business partner,estranged sibling,personal secretary,former apprentice,professional rival,old friend,landlord,family physician,named heir,creditor,neighbour,cousin".split(",")
MOT = ["stood to inherit", "was owed a large debt", "was about to be exposed", "had been passed over for promotion",
       "was jilted by the victim", "feared being dismissed", "had a decades-old grudge", "was cut out of a contract"]
AL = [("in the cloakroom", "the cloakroom ticket"), ("at the bar", "the bar tab"), ("on the telephone", "the exchange log"),
      ("in the kitchen", "the cook's night book"), ("at the front desk", "the signing-in ledger"),
      ("in the garden", "the gardener's lamp log"), ("in the card room", "the card-room scoresheet"),
      ("in the parlour", "the maid's rota")]
TRAITS = [("a smear of blue chalk", "dusts their cuffs with blue chalk"), ("a scent of violet pomade", "wears violet pomade"),
          ("a bent brass button", "is missing a brass coat button"), ("a pressed lily petal", "wears a lily in the lapel"),
          ("grey cat hairs", "keeps a grey cat"), ("a drop of green ink", "writes only in green ink"),
          ("flecks of red sealing wax", "seals letters with red wax"), ("a pearl bead", "has a broken pearl necklace")]
OTHER = ["is always punctual", "hums when nervous", "is left-handed", "takes snuff", "wears spectacles", "is very tall"]
SCN = ["A lamp lies overturned and one chair is pushed back.", "A teacup is cold and half full; the clock has stopped.",
       "Papers are scattered, but the strongbox is untouched.", "The window is latched from inside; the door was not forced.",
       "A coat hangs on the door and the fire has burned low."]

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
             rel=r.sample(REL, 5), mot=r.sample(MOT, 5), al=r.sample(AL, 5), oth=r.sample(OTHER, 5))
    d["title"] = "The %s %s" % (r.choice(ADJ), pl.split()[-1].title())
    return d

def broken(d): return (d["c"], d["rh2"])  # these two alibis fail; only c also has the trace

def suspect_page(d, i):
    T, w, vic = d["T"], d["w"], d["vic"]
    c = i == d["c"]; al = d["al"][i]
    if i in broken(d): stay = "from %s until well after %s" % (t(T - 45), t(T + 20))
    else: stay = "from %s to %s" % (t(T - 40), t(T + 30))
    trait = d["trait"] if i in (d["c"], d["decoy"]) else d["oth"][i]
    beh = {d["c"]: "calm, helpful, quick to suggest who else might have done it.", d["decoy"]: "nervous, sweating, avoids eye contact.",
           d["rh1"]: "angry and defensive; admits a quarrel with the victim.", d["rh2"]: "evasive and flustered; keeps checking the clock.",
           d["plain"]: "quiet and cooperative."}[i]
    say = ('"Whoever used %s on %s must be mad."' % (w, vic)) if c else '"I have no idea how it was done."'
    return ("<p><b>%s</b><br>%s</p><p>Motive: %s.</p><p>Alibi: \"I was %s %s. Check %s.\"</p>"
            "<p>Notes: %s Also, %s %s.</p><p>Said to police: %s</p>"
            % (d["s"][i], d["rel"][i].capitalize() + " of the victim", d["mot"][i], al[0], stay, al[1], beh.capitalize(),
               "this person", trait, say))

def page(d, slug):
    T, S, vic = d["T"], d["s"], d["vic"]
    if slug == "":
        return "Case %d" % d["n"], "<h2>%s</h2><p>%s, %s, is dead at %s.</p><p>Five suspects. One killer. Every page hides a clue.</p>" % (d["title"], vic, d["prof"], d["pl"])
    if slug == "briefing":
        return "Briefing", ("<p><b>%s</b>, %s, was found dead in %s at %s, at %s.</p><p>Died about: %s<br>Cause: %s<br>Weapon: %s</p>"
                            "<p><i>The weapon has not been disclosed to anyone in the household.</i></p>" % (vic, d["prof"], d["room"], d["pl"], t(T + 25), t(T), d["cause"], d["w"]))
    if slug == "scene": return "Crime Scene", "<p>%s</p><p>Nothing was forced. The killer was let in, or was already there.</p>" % d["scn"]
    if slug == "scene2":
        return "Scene: Details", "<p>Beside the body: <b>%s</b>.</p><p>The weapon, %s, was left behind. Whoever left the trace also stood close to the victim.</p>" % (d["trace"], d["w"])
    if slug == "suspects":
        return "Suspects", "<ul>%s</ul>" % "".join('<li><a class="b" href="/case/%d/s%d">%d. %s</a> (%s)</li>' % (d["n"], i + 1, i + 1, S[i], d["rel"][i]) for i in range(5))
    if slug[0] == "s" and slug[1:].isdigit() and 1 <= int(slug[1:]) <= 5:
        return "Suspect %s" % slug[1:], suspect_page(d, int(slug[1:]) - 1)
    if slug == "timeline":
        return "Timeline", ("<p>%s - %s and %s quarrel loudly.<br>%s - Smoke from the grate: %s burns a letter.<br>%s - Guests scatter to separate rooms.<br>"
                            "<b>%s - %s dies.</b><br>%s - Body found.<br>%s - Police arrive.</p>" % (t(T - 100), S[d["rh1"]], vic, t(T - 35), S[d["rh2"]], t(T - 60), t(T), vic, t(T + 25), t(T + 40)))
    if slug == "evidence":
        rows = "".join("<li>%s: %s - %s</li>" % (S[i], d["al"][i][1], "CONFLICT, shows departure at %s" % t(T - 15) if i in broken(d) else "consistent") for i in range(5))
        return "Evidence", "<p><b>A.</b> Trace at scene: %s.</p><p><b>B.</b> Alibi checks:</p><ul>%s</ul>" % (d["trace"], rows)
    if slug == "evidence2":
        return "Evidence: Notes", ("<p><b>C.</b> Ash fragment from the grate: \"...meet me in secret, as before...\"</p><p><b>D.</b> The quarrel concerned a bill, "
                                   "since settled in full.</p><p><b>E.</b> Reminder: nobody was told what weapon was used. Read what each suspect said.</p>")
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
        why = {d["decoy"]: "%s shares the scene trace, but their alibi record holds." % S[i],
               d["rh1"]: "%s quarrelled with the victim, but the bill was settled and the alibi holds." % S[i],
               d["rh2"]: "%s's alibi breaks, but only to hide a secret meeting, and they lack the trace." % S[i],
               d["plain"]: "%s has no trace and a solid alibi." % S[i]}[i]
        return html("WRONG ACCUSATION", "<p>That theory does not explain the evidence. %s</p><p><b>The killer was %s.</b></p>%s" % (why, S[c], solution(d)),
                    base + "/accuse", "/", menu)
    if k is None:
        rot = n % 3; opts = [("1", "The alibi record conflict"), ("2", "The loudest motive"), ("3", "The scene trace alone")]
        opts = opts[rot:] + opts[:rot]
        return html("CASE SOLVED", "<p>%s is the killer. One more question: what separated them from the other person with the same trace?</p><ul>%s</ul>" %
                    (S[c], "".join('<li><a class="b" href="%s/accuse/%d/%s">%s</a></li>' % (base, i + 1, kk, l) for kk, l in opts)), base + "/accuse", None, menu)
    head = "PERFECT DEDUCTION" if k == "1" else "CASE SOLVED"
    extra = "You found the key: only one trace-bearer lied about their whereabouts." if k == "1" else "Right culprit, but the alibi record is what truly decided it."
    return html(head, "<p>%s</p>%s" % (extra, solution(d)), base + "/accuse", "/random", menu)

def solution(d):
    S = d["s"]; c = d["c"]
    return ("<p>The scene held %s. Only %s and %s %s. %s's alibi record holds; %s's shows departure at %s. "
            "%s also named the weapon, %s, which nobody had been told.</p>" % (d["trace"], S[c], S[d["decoy"]], d["trait"].replace("their", "their"), S[d["decoy"]], S[c], t(d["T"] - 15), S[c], d["w"]))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
