"""Sources du site. Chaque source a plusieurs flux de secours : le premier qui répond gagne."""

def gnews(query):
    from urllib.parse import quote
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=fr&gl=FR&ceid=FR:fr"

JOURNAUX = [
    {
        "id": "figaro",
        "nom": "Le Figaro",
        "couleur": "#163860",
        "kiosko": [],
        "frontpages": "le-figaro",
        "flux": [
            "https://www.lefigaro.fr/rss/figaro_actualites.xml",
            "https://www.lefigaro.fr/rss/figaro_flash-actu.xml",
            gnews("site:lefigaro.fr when:1d"),
        ],
    },
    {
        "id": "monde",
        "nom": "Le Monde",
        "couleur": "#111111",
        "kiosko": [],
        "frontpages": "le-monde",
        "flux": [
            "https://www.lemonde.fr/rss/une.xml",
            gnews("site:lemonde.fr when:1d"),
        ],
    },
    {
        "id": "croix",
        "nom": "La Croix",
        "couleur": "#c8102e",
        "kiosko": ["lacroix", "la_croix"],
        "frontpages": "la-croix",
        "flux": [
            "https://www.la-croix.com/feeds/rss/site.xml",
            "https://www.la-croix.com/RSS/UNIVERS",
            gnews("site:la-croix.com when:1d"),
        ],
    },
    {
        "id": "equipe",
        "nom": "L'Équipe",
        "couleur": "#e2001a",
        "kiosko": ["l_equip", "lequipe", "l_equipe"],
        "frontpages": "l-equipe",
        "flux": [
            "https://dwh.lequipe.fr/api/edito/rss?path=/",
            gnews("site:lequipe.fr when:1d"),
        ],
    },
]

# Sections thématiques : tous les flux sont fusionnés, dédoublonnés,
# puis classés par importance (reprise par plusieurs médias, rang dans le flux, fraîcheur).
SECTIONS = [
    {
        "id": "monde",
        "titre": "Le monde ce matin",
        "sous_titre": "Les informations les plus importantes, partout dans le monde",
        "nb": 8,
        "flux": [
            "https://www.lemonde.fr/international/rss_full.xml",
            "https://www.france24.com/fr/rss",
            "https://www.rfi.fr/fr/rss",
            "https://www.francetvinfo.fr/monde.rss",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            gnews("monde international when:1d"),
            "https://news.google.com/rss/headlines/section/topic/WORLD?hl=fr&gl=FR&ceid=FR:fr",
        ],
    },
    {
        "id": "ia",
        "titre": "Intelligence artificielle",
        "sous_titre": "Modèles, entreprises, régulation, recherche",
        "nb": 8,
        "flux": [
            gnews("intelligence artificielle when:1d"),
            gnews("OpenAI OR Anthropic OR \"Google DeepMind\" OR Mistral AI when:2d"),
            "https://www.numerama.com/tech/intelligence-artificielle/feed/",
            "https://siecledigital.fr/intelligence-artificielle/feed/",
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "https://techcrunch.com/category/artificial-intelligence/feed/",
        ],
    },
    {
        "id": "droit",
        "titre": "Actualité juridique",
        "sous_titre": "Libertés fondamentales, grandes juridictions, culture juridique pour le CRFPA",
        "nb": 10,
        "flux": [
            gnews("\"Conseil constitutionnel\" France -Cameroun -Sénégal -Mauritanie -Gabon -Bénin -Côte when:3d"),
            gnews("\"Conseil d'État\" décision when:3d"),
            gnews("\"Cour de cassation\" arrêt when:3d"),
            gnews("CEDH OR \"Cour européenne des droits de l'homme\" when:3d"),
            gnews("\"libertés fondamentales\" OR \"liberté d'expression\" OR QPC when:3d"),
            "https://www.dalloz-actualite.fr/rss.xml",
            "https://www.village-justice.com/articles/spip.php?page=backend",
            "https://www.conseil-constitutionnel.fr/rss.xml",
        ],
        "mots_libertes": [
            "liberté", "libertés", "droit fondamental", "droits fondamentaux", "cedh",
            "convention européenne", "qpc", "conseil constitutionnel", "laïcité",
            "vie privée", "expression", "manifestation", "garde à vue", "asile",
            "discrimination", "dignité", "référé-liberté", "défenseur des droits",
            "droits de l'homme", "censure", "inconstitutionnel",
        ],
    },
]
