"""Sonde temporaire : unes en haute définition."""
import re, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
def get(u, ref=None):
    h = {"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"}
    if ref: h["Referer"] = ref
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=20); d = r.read()
        return r.status, len(d), d
    except urllib.error.HTTPError as e:
        return e.code, 0, b""
    except Exception as e:
        return type(e).__name__, 0, b""
for slug in ("le-monde", "le-figaro"):
    page = get(f"https://www.frontpages.com/{slug}/")[2].decode("utf-8", "ignore")
    urls = sorted(set(re.findall(r'(?:https://www\.frontpages\.com)?/[gt]/\d{4}/\d\d/\d\d/' + slug + r'-[^"\'\s)]+', page)))
    print(slug, urls[:6])
    for m in re.finditer(r'.{0,150}' + slug + r'-[a-z0-9]+\.webp.{0,150}', page):
        print("   CTX", m.group(0)[:300]); break
    for u in urls[:4]:
        u = u if u.startswith("http") else "https://www.frontpages.com" + u
        for ref in (None, f"https://www.frontpages.com/{slug}/"):
            st, n, _ = get(u, ref); print("   ", st, n, "ref" if ref else "   ", u)
page = get("https://kiosque.lefigaro.fr/")[2].decode("utf-8", "ignore")
for m in re.finditer(r'.{0,300}milibris\.com/thumbnail/issue/[^"]+.{0,200}', page):
    print("FIG CTX", m.group(0)[:500]); break
ids = re.findall(r'milibris\.com/thumbnail/issue/([0-9a-f-]+)/front/([^"\']+)', page)
print("FIG ids", ids[:3])
if ids:
    i = ids[0][0]
    for v in ("catalog-cover-icon.png", "catalog-cover.png", "catalog-cover-large.png", "catalog-cover-large.jpeg", "catalog-cover-medium.png", "release-cover.png", "large.jpeg"):
        st, n, _ = get(f"https://static.milibris.com/thumbnail/issue/{i}/front/{v}"); print("   ", st, n, v)
for u in ("https://journal.lemonde.fr/", "https://www.lemonde.fr/journal-du-jour/"):
    st, n, d = get(u); print("LM", u, st, n, d[:600])
