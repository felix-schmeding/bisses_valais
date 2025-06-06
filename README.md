# bisses_valais
Developpement d'un modèle conceptuel pour les bisses valaisans

# Environnement python

Les librairies nécéssaires sont:
- numpy
- pandas
- geopandas
- dash
- plotly

# Données

Pour pouvoir traiter les données, il suffit de suivre les étapes suivantes:
- Dans QGIS: dupliquer une couche template du format de donnée adaptée
- modifier le json propre au bisse en ajouter un dict avec comme "key" la même que dans le json donnees.json (/template)
- ajouter les infos supplémentaire (date, chemin de sauvegarde, ...)


### Variation temporelle

**À TRAITER PLUS TARD**

À préciser:
- type de variation: jour, mois, saison, année

Exemples de données temporelles pour aider à bien faire la structure:
- demande en eau: dépend des données metéorologiques. On peut classifier les conditions en sec, moyen, humide
- demande en eau: la demande en eau dépend aussi du mois, de plus ce sera différent suivant la culture et de l'age de la plantation
**On laisse une valeur générique pour le type de culture et l'on adapte à l'age de la plantation**
- eau disponible dans les torrents: **out of scope**
- température de l'eau/débit et autre mesure de capteurs. Large plage de variation temporelle, peuvent même être en continue

### Autres

Peut aussi aller dans format des données

- interview, sous forme papier/audio/vidéo
- Photos
- Ressources en ligne

