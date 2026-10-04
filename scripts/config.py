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
        "milibris": "https://kiosque.lefigaro.fr/",
        "frontpages": "le-figaro",
        "sources_une": ["milibris", "frontpages"],
        "sans_parution": [6],  # pas d'édition le dimanche
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
        "sources_une": ["frontpages"],
        "decalage_frontpages": 1,  # paraît l'après-midi, daté du lendemain
        "edition_double_dimanche": True,  # l'édition datée du dimanche vaut aussi pour le lundi
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
        "titre": "Actualité principale",
        "sous_titre": "Les informations les plus importantes, partout dans le monde",
        "nb": 6,
        "score_min": 2.0,  # reprise par au moins deux sources
        "mots_exclus": ["que faire", "horoscope", "meteo", "recette", "bon plan", "jeu concours", "programme tv", "people"],
        "flux": [
            "https://www.lemonde.fr/international/rss_full.xml",
            "https://www.france24.com/fr/rss",
            "https://www.rfi.fr/fr/rss",
            "https://www.francetvinfo.fr/monde.rss",
            gnews("monde international when:1d"),
            "https://news.google.com/rss/headlines/section/topic/WORLD?hl=fr&gl=FR&ceid=FR:fr",
        ],
    },
    {
        "id": "ia",
        "titre": "Intelligence artificielle",
        "sous_titre": "Modèles, entreprises, régulation, recherche",
        "nb": 5,
        "mots_requis": [" ia ", " ia,", " ia.", "l'ia", "d'ia", "intelligence artificielle", " ai ", " ai,", "a.i.", "openai", "anthropic", "claude",
                        "chatgpt", "gemini", "mistral", "deepmind", "llm", "copilot", "nvidia", "agent ia", "modele de langage", "machine learning", "artificial intelligence"],
        "mots_exclus": ["meilleurs outils", "bon plan", "promo", "code promo", "test :", "comparatif", "horoscope", "fete du livre"],
        "flux": [
            gnews("intelligence artificielle when:1d"),
            gnews("OpenAI OR Anthropic OR \"Google DeepMind\" OR \"Mistral AI\" lang:fr when:2d"),
            "https://www.numerama.com/tech/intelligence-artificielle/feed/",
            "https://siecledigital.fr/intelligence-artificielle/feed/",
        ],
    },
    {
        "id": "droit",
        "titre": "Actualité juridique",
        "sous_titre": "Libertés fondamentales, grandes juridictions, culture juridique pour le CRFPA",
        "nb": 6,
        "mots_requis": ["conseil constitutionnel", "conseil d'etat", "cour de cassation", "cedh", "cour europeenne", "cjue", "qpc",
                        "jurisprudence", "revirement", "liberte", "droits de l'homme", "droit fondamental", "droits fondamentaux",
                        "garde a vue", "censure", "inconstitutionnel", "refere-liberte", "defenseur des droits", "laicite", "vie privee"],
        "mots_exclus": ["que faire", "nuit du droit", "rendez-vous", "agenda", "sortir", "pourquoi saisir", "voici ce qu", "ce qu'il faut savoir", "tout savoir", "vos droits", "peut-on ", "puis-je", "salon", "colloque", "conference", "concours", "barreau", "avocats :", "profession", "comment contester", "comment ", " ma maison", "mon ", "ce que l'arret", "recue au", "visite", "classe de",
                        "cameroun", "senegal", "mauritanie", "gabon", "benin", "cote d'ivoire", "togo", "mali", "burkina", "guinee",
                        "congo", "tchad", "madagascar", "algerie", "maroc", "tunisie conseil constitutionnel", "football", "ligue 1"],
        # Sites de cabinets et conseils pratiques : pas de l'actualité juridique
        "sources_exclues": ["avocat", "cabinet", "village de la justice", "juritravail", "legavox", "dossierfamilial"],
        "flux": [
            gnews("\"Conseil constitutionnel\" France -Cameroun -Sénégal -Mauritanie -Gabon -Bénin -Côte when:3d"),
            gnews("\"Conseil d'État\" décision when:3d"),
            gnews("\"Cour de cassation\" arrêt when:3d"),
            gnews("CEDH OR \"Cour européenne des droits de l'homme\" when:3d"),
            gnews("\"libertés fondamentales\" OR \"liberté d'expression\" OR QPC when:3d"),
            "https://www.dalloz-actualite.fr/rss.xml",
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
