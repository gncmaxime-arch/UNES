#!/usr/bin/env python3
"""Construit l'édition du jour.

1. Collecte : flux RSS des journaux et des sections + image de la une (Kiosko).
2. Écrit data/brut.json (matière première, lue ensuite par la routine Claude).
3. Fusionne data/editorial.json s'il date du jour (sélection et résumés rédigés par Claude).
4. Génère site/index.html.

Uniquement la bibliothèque standard : rien à installer.
"""
import datetime as dt
import email.utils
import html
import json
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from config import JOURNAUX, SECTIONS  # noqa: E402
from render import render  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
DATA = RACINE / "data"
PARIS = ZoneInfo("Europe/Paris")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
MAINTENANT = dt.datetime.now(PARIS)
AUJOURDHUI = MAINTENANT.date()


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------- Flux RSS / Atom ----------

def texte(s, n=None):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    if n and len(s) > n:
        s = s[: n - 1].rsplit(" ", 1)[0] + "…"
    return s


def date_item(s):
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(PARIS)


def parse_flux(raw, url):
    root = ET.fromstring(raw)
    items = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        champs = {}
        image = None
        for c in el:
            t = c.tag.split("}")[-1]
            if t == "link":
                champs["link"] = c.get("href") or (c.text or "").strip()
            elif t in ("content", "thumbnail") and c.get("url") and not image:
                image = c.get("url")
            elif t == "enclosure" and (c.get("type") or "").startswith("image"):
                image = c.get("url")
            elif t == "source":
                champs["source"] = (c.text or "").strip()
            else:
                champs.setdefault(t, c.text or "")
        titre = texte(champs.get("title"))
        if not titre:
            continue
        source = champs.get("source") or ""
        if "news.google.com" in url and " - " in titre:
            titre, _, src = titre.rpartition(" - ")
            source = source or src
        items.append({
            "titre": titre,
            "lien": champs.get("link", ""),
            "resume": texte(champs.get("description") or champs.get("summary") or champs.get("encoded"), 260),
            "date": (date_item(champs.get("pubDate") or champs.get("published") or champs.get("updated") or champs.get("date")) or MAINTENANT).isoformat(),
            "source": source,
            "image": image,
        })
    return items


def lire_flux(url):
    try:
        items = parse_flux(get(url), url)
        log(f"  ok  {len(items):3d}  {url[:110]}")
        return items
    except Exception as e:  # un flux en panne ne doit jamais casser l'édition
        log(f"  ERR {type(e).__name__}: {e}  {url[:110]}")
        return []


def premier_flux(urls):
    for u in urls:
        items = lire_flux(u)
        if items:
            return items, u
    return [], None


def domaine(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else ""


# ---------- Classement par importance ----------

VIDES = set("le la les un une des de du d l et en à au aux pour par sur dans avec sans est sont a ont qui que quoi ne pas plus se sa son ses leur leurs ce cette ces il elle ils elles on nous vous après avant face contre entre the of to in and for on with is are as at by from".split())


def mots(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r"[a-z0-9]{3,}", t) if w not in VIDES}


def classer(listes, nb, recents_h=36):
    """listes : une liste d'items par flux. Regroupe les sujets proches et note chaque groupe."""
    groupes = []
    for items in listes:
        for rang, it in enumerate(items[:40]):
            d = dt.datetime.fromisoformat(it["date"])
            age_h = (MAINTENANT - d).total_seconds() / 3600
            if age_h > recents_h:
                continue
            m = mots(it["titre"])
            if len(m) < 2:
                continue
            score = 1.0 / (1 + rang * 0.15) + max(0, 1 - age_h / recents_h) * 0.6
            for g in groupes:
                inter = len(m & g["mots"])
                if inter >= 3 or inter / max(1, min(len(m), len(g["mots"]))) >= 0.5:
                    g["score"] += score + 1.2  # reprise par une autre source : signal fort
                    g["sources"].add(it.get("source") or domaine(it["lien"]))
                    g["mots"] |= m
                    if not g["item"]["resume"] and it["resume"]:
                        g["item"]["resume"] = it["resume"]
                    break
            else:
                groupes.append({"item": dict(it), "mots": set(m), "score": score,
                                "sources": {it.get("source") or domaine(it["lien"])}})
    groupes.sort(key=lambda g: g["score"], reverse=True)
    out = []
    for g in groupes[:nb]:
        it = g["item"]
        it["reprises"] = len(g["sources"])
        it["source"] = it.get("source") or domaine(it["lien"])
        out.append(it)
    return out


# ---------- Unes (images) ----------

def slugs_kiosko():
    """Liste les identifiants de journaux français connus de Kiosko (pour ne pas dépendre de slugs devinés)."""
    trouves = set()
    for url in ("https://www.kiosko.net/fr/", "https://www.kiosko.net/fr/geo/Paris.html", "https://fr.kiosko.net/fr/"):
        try:
            page = get(url).decode("utf-8", "ignore")
        except Exception as err:
            log(f"  kiosko {url}: {type(err).__name__}")
            continue
        trouves |= set(re.findall(r"/fr/np/([a-z0-9_]+)\.html", page))
        trouves |= set(re.findall(r"img\.kiosko\.net/\d+/\d+/\d+/fr/([a-z0-9_]+)\.\d+\.jpg", page))
    log(f"  kiosko : {len(trouves)} journaux repérés : {' '.join(sorted(trouves))[:900]}")
    return trouves


def une_frontpages(j):
    """frontpages.com expose la une du jour en og:image (…/g/AAAA/MM/JJ/<nom>.webp.jpg)."""
    try:
        page = get(f"https://www.frontpages.com/{j['frontpages']}/").decode("utf-8", "ignore")
    except Exception as err:
        log(f"  frontpages {j['nom']}: {type(err).__name__}")
        return None
    slug = re.escape(j["frontpages"])
    m = re.search(rf'((?:https://www\.frontpages\.com)?/g/(\d{{4}})/(\d{{2}})/(\d{{2}})/{slug}-[^"\'\s)]+)', page)
    if not m:
        log(f"  frontpages {j['nom']}: image non repérée dans la page")
        return None
    url, a, mo, d = m.groups()
    if url.startswith("/"):
        url = "https://www.frontpages.com" + url
    return telecharger_frontpages(j, url, a, mo, d)


def telecharger_frontpages(j, url, a, mo, d):
    try:
        data = get(url, timeout=20)
    except Exception as err:
        log(f"  frontpages {j['nom']}: {type(err).__name__} sur {url}")
        return None
    ext = "jpg" if data[:2] == b"\xff\xd8" else "webp" if data[:4] == b"RIFF" else None
    if not ext or len(data) < 15000:
        log(f"  frontpages {j['nom']}: fichier inattendu ({len(data)} octets) {url}")
        return None
    (SITE / "unes").mkdir(parents=True, exist_ok=True)
    nom = f"unes/{j['id']}.{ext}"
    (SITE / nom).write_bytes(data)
    log(f"  une {j['nom']}: {url}")
    return {"fichier": nom, "date": f"{a}-{mo}-{d}", "source": url}


def chercher_une(j, connus):
    une = une_kiosko(j, connus) if j["kiosko"] else None
    recente = AUJOURDHUI - dt.timedelta(days=1)
    if une and une["date"] >= recente.isoformat():
        return une
    autre = une_frontpages(j) if j.get("frontpages") else None
    if autre and (not une or autre["date"] > une["date"]):
        return autre
    if not une:
        log(f"  une {j['nom']}: introuvable")
    return une


def une_kiosko(j, connus):
    """Kiosko publie la une sous img.kiosko.net/AAAA/MM/JJ/fr/<slug>.750.jpg.
    Le Monde est daté du lendemain, Le Figaro ne paraît pas le dimanche :
    on essaie demain, aujourd'hui, puis jusqu'à trois jours en arrière."""
    cle = j["id"]
    slugs = list(dict.fromkeys(j["kiosko"] + sorted(s for s in connus if cle in s and "magazine" not in s)))
    jours = [AUJOURDHUI + dt.timedelta(days=k) for k in (1, 0, -1, -2, -3)]
    for jour in jours:
        for slug in slugs:
            url = f"https://img.kiosko.net/{jour:%Y/%m/%d}/fr/{slug}.750.jpg"
            try:
                data = get(url, timeout=15)
            except Exception:
                continue
            if len(data) > 15000 and data[:2] == b"\xff\xd8":
                (SITE / "unes").mkdir(parents=True, exist_ok=True)
                nom = f"unes/{j['id']}.jpg"
                (SITE / nom).write_bytes(data)
                log(f"  une {j['nom']}: {url}")
                return {"fichier": nom, "date": jour.isoformat(), "source": url}
    log(f"  kiosko {j['nom']}: rien (slugs essayés : {slugs})")
    return None


# ---------- Assemblage ----------

def collecter():
    log("== Journaux")
    with ThreadPoolExecutor(8) as ex:
        flux_j = list(ex.map(lambda j: premier_flux(j["flux"]), JOURNAUX))
        connus = slugs_kiosko()
        unes = list(ex.map(lambda j: chercher_une(j, connus), JOURNAUX))
    journaux = []
    for j, (items, url), une in zip(JOURNAUX, flux_j, unes):
        recents = [i for i in items if (MAINTENANT - dt.datetime.fromisoformat(i["date"])).days < 2] or items
        journaux.append({"id": j["id"], "nom": j["nom"], "couleur": j["couleur"], "une": une,
                         "articles": recents[:6], "flux_utilise": url})
    log("== Sections")
    sections = []
    for s in SECTIONS:
        with ThreadPoolExecutor(8) as ex:
            listes = list(ex.map(lire_flux, s["flux"]))
        items = classer(listes, s["nb"], recents_h=72 if s["id"] == "droit" else 36)
        if s.get("mots_libertes"):
            for it in items:
                t = (it["titre"] + " " + it["resume"]).lower()
                it["libertes"] = any(k in t for k in s["mots_libertes"])
        sections.append({"id": s["id"], "titre": s["titre"], "sous_titre": s["sous_titre"], "items": items})
    return {"date": AUJOURDHUI.isoformat(), "genere": MAINTENANT.isoformat(timespec="minutes"),
            "journaux": journaux, "sections": sections}


def fusion_editorial(ed):
    """La routine Claude écrit data/editorial.json ; on ne l'utilise que s'il date du jour."""
    f = DATA / "editorial.json"
    if not f.exists():
        return ed
    try:
        e = json.loads(f.read_text())
    except ValueError as err:
        log(f"editorial.json illisible : {err}")
        return ed
    if e.get("date") != ed["date"]:
        log(f"editorial.json daté du {e.get('date')} : ignoré")
        return ed
    log("== Éditorial Claude fusionné")
    ed["editorial"] = e
    return ed


def main():
    SITE.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    if "--rendu-seul" in sys.argv:  # régénère la page sans recollecter (après la routine Claude)
        ed = json.loads((DATA / "brut.json").read_text())
    else:
        ed = collecter()
        (DATA / "brut.json").write_text(json.dumps(ed, ensure_ascii=False, indent=1))
    ed = fusion_editorial(ed)
    (SITE / "index.html").write_text(render(ed))
    log("== site/index.html écrit")


if __name__ == "__main__":
    main()
