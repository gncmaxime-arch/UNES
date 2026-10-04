"""Sonde temporaire 2 : identifier l'édition quotidienne du Figaro sur kiosque.lefigaro.fr + vignettes @2x."""
import re, urllib.request, struct
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20); return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", type(e).__name__), b""
def dims(d):
    if d[:2] == b"\xff\xd8":
        i = 2
        while i < len(d):
            if d[i] != 0xFF: break
            m = d[i+1]; L = struct.unpack(">H", d[i+2:i+4])[0]
            if m in (0xC0, 0xC2): return struct.unpack(">HH", d[i+5:i+9])[::-1]
            i += 2 + L
    if d[:4] == b"RIFF" and d[12:16] == b"VP8 ": return struct.unpack("<HH", d[26:30])
    if d[:4] == b"RIFF" and d[12:16] == b"VP8L":
        b = d[21:25]; v = int.from_bytes(b, "little"); return ((v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1)
    if d[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", d[16:24])
    return None
st, p = get("https://kiosque.lefigaro.fr/"); page = p.decode("utf-8", "ignore")
for m in list(re.finditer(r'milibris\.com/thumbnail/issue/([0-9a-f-]+)/front/', page))[:6]:
    a = max(0, m.start() - 900); ctx = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", page[a:m.end() + 600]))
    print("ISSUE", m.group(1)); print("   ", ctx[-1200:])
    s2, d = get(f"https://static.milibris.com/thumbnail/issue/{m.group(1)}/front/catalog-cover-large.jpeg"); print("    large", s2, len(d), dims(d))
for slug in ("le-monde", "le-figaro", "la-croix", "l-equipe"):
    st, p = get(f"https://www.frontpages.com/{slug}/"); page = p.decode("utf-8", "ignore")
    m = re.search(r'/g/(\d{4}/\d\d/\d\d)/(' + slug + r'-[a-z0-9]+)\.webp', page)
    if m:
        for v in (f"/t/{m.group(1)}/{m.group(2)}.webp", f"/t/{m.group(1)}/{m.group(2)}@2x.webp"):
            s2, d = get("https://www.frontpages.com" + v); print(slug, s2, len(d), dims(d), v)
for u in ("https://img.kiosko.net/2026/10/05/fr/lacroix.750.jpg", "https://img.kiosko.net/2026/10/04/fr/l_equip.750.jpg"):
    s2, d = get(u); print("kiosko", s2, len(d), dims(d), u)
