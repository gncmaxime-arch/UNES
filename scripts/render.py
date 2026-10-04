"""Transforme l'édition (dict) en page HTML autonome."""
import datetime as dt
import html
import json

from config import JOURNAUX

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
ICONES = {"monde": "◍", "ia": "◇", "droit": "§"}


def e(s):
    return html.escape(str(s or ""), quote=True)


def date_longue(iso):
    d = dt.date.fromisoformat(iso[:10])
    return f"{JOURS[d.weekday()]} {d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]} {d.year}"


def heure(iso):
    try:
        return dt.datetime.fromisoformat(iso).strftime("%H:%M")
    except ValueError:
        return ""


def lien(it, contenu, cls=""):
    if it.get("lien"):
        return f'<a class="{cls}" href="{e(it["lien"])}" target="_blank" rel="noopener">{contenu}</a>'
    return f'<span class="{cls}">{contenu}</span>'


def legende_edition(j, une, jour):
    """Mention sous la une quand ce n'est pas l'édition du jour, avec la raison si on la connaît."""
    if not une:
        return ""
    conf = next((c for c in JOURNAUX if c["id"] == j["id"]), {})
    ed = dt.date.fromisoformat(une["date"][:10])
    auj = dt.date.fromisoformat(jour)
    couvre = ed + dt.timedelta(days=1) if conf.get("edition_double_dimanche") and ed.weekday() == 6 else ed
    if couvre >= auj:
        return ""
    texte = f"édition du {date_longue(ed.isoformat()).rsplit(' ', 1)[0]}"
    if auj.weekday() in conf.get("sans_parution", []) and (auj - ed).days == 1:
        texte += " · pas de parution le " + JOURS[auj.weekday()]
    return f' <small>· {e(texte)}</small>'


def carte_une(j, i, jour):
    une = j.get("une")
    legende = e(j["nom"]) + legende_edition(j, une, jour)
    if une:
        visuel = (f'<img src="{e(une["fichier"])}?v={e(une["date"])}" alt="Une de {e(j["nom"])}" '
                  f'loading="{"eager" if i < 2 else "lazy"}" decoding="async">')
    else:
        titre = j["articles"][0]["titre"] if j.get("articles") else "Une indisponible ce matin"
        visuel = (f'<div class="une-vide"><span class="une-vide-nom">{e(j["nom"])}</span>'
                  f'<span class="une-vide-titre">{e(titre)}</span></div>')
    return (f'<figure class="une" data-i="{i}" style="--c:{e(j["couleur"])}" tabindex="0" '
            f'aria-label="{e(j["nom"])}">{visuel}<figcaption>{legende}</figcaption></figure>')


def panneau_journal(j, ed_j, i):
    articles = j.get("articles") or []
    points = ""
    if ed_j:
        if ed_j.get("resume"):
            points += f'<p class="j-resume">{e(ed_j["resume"])}</p>'
        if ed_j.get("points"):
            points += "<ul class=\"j-points\">" + "".join(
                f"<li>{e(p)}</li>" for p in ed_j["points"]) + "</ul>"
    liste = "".join(
        f'<li>{lien(a, e(a["titre"]), "j-art")}'
        + (f'<p>{e(a["resume"])}</p>' if a.get("resume") and not ed_j else "")
        + "</li>"
        for a in articles[: (4 if ed_j else 6)])
    if not liste and not points:
        liste = "<li class=\"muet\">Flux indisponible ce matin.</li>"
    titre_liste = "<h4>Les articles</h4>" if ed_j else ""
    return (f'<article class="journal{" actif" if i == 0 else ""}" data-i="{i}" style="--c:{e(j["couleur"])}">'
            f'<header><span class="pastille"></span><h3>{e(j["nom"])}</h3></header>'
            f'{points}{titre_liste}<ol class="j-liste">{liste}</ol></article>')


def details_item(it):
    """Ce qui ne s'affiche qu'au toucher : résumé, enjeu, angle CRFPA, lien."""
    corps = ""
    if it.get("resume"):
        corps += f"<p>{e(it['resume'])}</p>"
    if it.get("pourquoi"):
        corps += f'<p class="pourquoi"><b>Pourquoi c\'est important</b> {e(it["pourquoi"])}</p>'
    if it.get("angle_crfpa"):
        corps += f'<p class="crfpa"><b>Angle CRFPA</b> {e(it["angle_crfpa"])}</p>'
    if it.get("lien"):
        corps += f'<a class="lire" href="{e(it["lien"])}" target="_blank" rel="noopener">Lire l\'article →</a>'
    return corps


def bloc_section(s, items_ed):
    items = items_ed if items_ed is not None else s["items"]
    if not items:
        corps = '<p class="muet">Rien de neuf dans les sources ce matin.</p>'
    else:
        une, reste = items[0], items[1:]
        meta = " · ".join(x for x in [e(une.get("source")), heure(une.get("date", ""))] if x)
        lib = '<span class="badge lib">Libertés fondamentales</span>' if une.get("libertes") else ""
        resume = f"<p>{e(une['resume'])}</p>" if une.get("resume") else ""
        extra = ""
        if une.get("pourquoi"):
            extra += f'<p class="pourquoi"><b>Pourquoi c\'est important</b> {e(une["pourquoi"])}</p>'
        if une.get("angle_crfpa"):
            extra += f'<p class="crfpa"><b>Angle CRFPA</b> {e(une["angle_crfpa"])}</p>'
        vedette = (f'<article class="vedette reveal"><div class="vedette-in">'
                   f'<div class="v-tete"><span class="v-label">À la une</span>{lib}</div>'
                   f'<h3>{lien(une, e(une["titre"]))}</h3>{resume}{extra}'
                   f'<div class="meta">{meta}</div></div></article>')
        lignes = []
        for k, it in enumerate(reste, start=2):
            puce = '<span class="pt-lib" title="Libertés fondamentales"></span>' if it.get("libertes") else ""
            lignes.append(
                f'<details class="ligne reveal" style="--d:{(k - 2) * 40}ms">'
                f'<summary><span class="num">{k}</span><span class="l-txt"><span class="l-titre">{e(it["titre"])}</span>'
                f'<span class="l-meta">{puce}{e(it.get("source"))}</span></span><span class="plus" aria-hidden="true"></span></summary>'
                f'<div class="l-corps">{details_item(it)}</div></details>')
        corps = f'{vedette}<div class="liste">{"".join(lignes)}</div>'
    return (f'<section class="section" id="{e(s["id"])}">'
            f'<header class="s-tete reveal"><span class="s-icone">{ICONES.get(s["id"], "•")}</span>'
            f'<div><h2>{e(s["titre"])}</h2><p>{e(s["sous_titre"])}</p></div></header>{corps}</section>')


def bloc_notion(n):
    if not n:
        return ""
    cite = f"<cite>{e(n['reference'])}</cite>" if n.get("reference") else ""
    return (f'<aside class="notion reveal"><div class="notion-label">Culture juridique du jour</div>'
            f'<h3>{e(n.get("titre"))}</h3><p>{e(n.get("texte"))}</p>'
            f'{cite}</aside>')


def render(ed):
    edito = ed.get("editorial") or {}
    ed_journaux = edito.get("journaux") or {}
    ed_sections = edito.get("sections") or {}
    journaux = ed["journaux"]
    cartes = "".join(carte_une(j, i, ed["date"]) for i, j in enumerate(journaux))
    panneaux = "".join(panneau_journal(j, ed_journaux.get(j["id"]), i) for i, j in enumerate(journaux))
    points = "".join(f'<button class="point{" actif" if i == 0 else ""}" data-i="{i}" '
                     f'aria-label="{e(j["nom"])}"></button>' for i, j in enumerate(journaux))
    sections = ""
    for s in ed["sections"]:
        sections += bloc_section(s, ed_sections.get(s["id"]))
        if s["id"] == "droit":
            sections = sections[: -len("</section>")] + bloc_notion(edito.get("notion")) + "</section>"
    chapo = f'<p class="edito">{e(edito["edito"])}</p>' if edito.get("edito") else ""
    with open(__file__.replace("render.py", "page.html"), encoding="utf-8") as f:
        page = f.read()
    return (page
            .replace("{{DATE}}", e(date_longue(ed["date"])).capitalize())
            .replace("{{DATE_ISO}}", e(date_longue(ed["date"])))
            .replace("{{GENERE}}", e(heure(ed["genere"])))
            .replace("{{EDITO}}", chapo)
            .replace("{{CARTES}}", cartes)
            .replace("{{POINTS}}", points)
            .replace("{{PANNEAUX}}", panneaux)
            .replace("{{SECTIONS}}", sections)
            .replace("{{CLAUDE}}", "Sélection et résumés rédigés par Claude" if edito else "Sélection automatique"))
