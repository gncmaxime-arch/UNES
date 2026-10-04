"""Sonde temporaire : où trouver les unes du Figaro et du Monde ?"""
import re, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
PAGES = [
    "https://www.frontpages.com/le-figaro/", "https://www.frontpages.com/le-monde/", "https://www.frontpages.com/l-equipe/",
    "https://www.kiosko.net/fr/np/lefigaro.html", "https://www.kiosko.net/fr/np/le_monde.html", "https://www.kiosko.net/fr/np/lemonde.html",
    "https://www.epresse.fr/journal/le-figaro", "https://www.epresse.fr/journal/le-monde",
    "https://kiosque.lefigaro.fr/", "https://journal.lemonde.fr/", "https://www.lemonde.fr/journal-du-jour/",
    "https://www.pressreader.com/france/le-figaro", "https://www.pressreader.com/france/le-monde",
    "https://www.relay.com/presse/quotidiens/le-figaro", "https://www.lekiosque.fr/",
    "https://www.journaux.fr/le-figaro_quotidiens_15_132.html",
]
for u in PAGES:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20)
        h = r.read().decode("utf-8", "ignore")
        imgs = re.findall(r'(?:og:image"\s+content="|src="|data-src=")([^"]+\.(?:jpe?g|webp|png)[^"]*)', h)
        imgs = [i for i in imgs if re.search(r"figaro|monde|equipe|une|cover|couv|2026", i, re.I)][:6]
        print("OK ", r.status, u, len(h)); [print("     ", i[:200]) for i in imgs]
    except Exception as e:
        print("ERR", u, type(e).__name__, e)
