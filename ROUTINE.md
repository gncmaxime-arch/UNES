# Consignes de la routine Claude du matin

Chaque matin, après la collecte automatique (GitHub Actions), une routine Claude lit
`data/brut.json`, rédige la partie éditoriale et pousse `data/editorial.json` sur `main`.
Ce push relance l'Action, qui régénère le site avec ce contenu.
Si la routine échoue, le site reste en ligne avec la sélection automatique.

## Étapes

1. Récupérer le dépôt à jour (`main`) et lire `data/brut.json`.
   Si sa `date` n'est pas celle du jour (heure de Paris), attendre quelques minutes et relire, deux fois au plus.
2. Compléter si besoin avec la recherche web (WebSearch) : les flux ne disent pas tout.
3. Écrire `data/editorial.json` au format ci-dessous, en français, ton sobre et factuel.
4. Commit « Éditorial du AAAA-MM-JJ » et push sur `main`.

## Règles de rédaction

- **Journaux** : pour chacun, un résumé de 2 phrases de ce qui fait sa une aujourd'hui,
  puis 3 à 4 points clés tirés de ses articles du jour. Ne rien inventer qui ne figure pas dans les sources.
- **Monde** : les 6 à 8 informations les plus importantes dans le monde (pas seulement en France).
  Classer par importance réelle (conséquences, ampleur), pas par nombre de clics.
  Un champ `pourquoi` d'une phrase : pourquoi c'est important.
- **IA** : 5 à 8 actualités marquantes (modèles, entreprises, régulation, recherche, usages).
  Écarter les articles promotionnels et les listes de « meilleurs outils ».
- **Droit** : 6 à 10 actualités, priorité aux décisions du Conseil constitutionnel, du Conseil d'État,
  de la Cour de cassation, de la CEDH et de la CJUE, aux lois et aux libertés fondamentales.
  `libertes: true` quand le sujet touche une liberté fondamentale.
  `angle_crfpa` : une phrase qui rattache l'info au programme (notion, principe, grand arrêt, article),
  utile pour le grand oral et la note de synthèse.
- **Notion du jour** : une notion de culture juridique ou un grand arrêt / une grande décision,
  différente chaque jour (consulter `data/archives/` et les éditoriaux précédents dans l'historique git
  pour ne pas se répéter). 3 à 5 phrases, référence exacte. Ne citer qu'une référence dont on est certain.
- Chaque item garde le `lien` d'origine. Pas de lien inventé.

## Format de `data/editorial.json`

```json
{
  "date": "AAAA-MM-JJ",
  "edito": "3 phrases : l'essentiel de la journée.",
  "journaux": {
    "figaro": {"resume": "…", "points": ["…", "…", "…"]},
    "monde":  {"resume": "…", "points": ["…"]},
    "croix":  {"resume": "…", "points": ["…"]},
    "equipe": {"resume": "…", "points": ["…"]}
  },
  "sections": {
    "monde": [{"titre": "…", "resume": "…", "pourquoi": "…", "lien": "https://…", "source": "…", "date": "ISO 8601"}],
    "ia":    [{"titre": "…", "resume": "…", "lien": "https://…", "source": "…", "date": "ISO 8601"}],
    "droit": [{"titre": "…", "resume": "…", "libertes": true, "angle_crfpa": "…", "lien": "https://…", "source": "…", "date": "ISO 8601"}]
  },
  "notion": {"titre": "…", "texte": "…", "reference": "…"}
}
```
