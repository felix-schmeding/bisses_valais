# bisses_valais
Developpement d'un modèle conceptuel pour les bisses valaisans

# Données

Pour pouvoir traiter les données, il suffit de suivre les étapes suivantes:
- dupliquer une couche template du format de donnée adaptée
- modifier le json propre au bisse en ajouter un dict avec comme "key" la même que dans le json donnees.json (/template)
- ajouter les infos supplémentaire (date, chemin de sauvegarde, ...)

## Types de données

Si il y a plus que un seul indicateur par set de données recolté, 
3 options:
- l'entrée "type_donnee" est une liste
(faire que ce soit toujours une liste, quitte à avoir une seule entrée???)
- **avoir une entrée dans le json par variable**
    Il faut spécifier les colonnes qu'on veut 
- avoir un dict avec les infos sur chaque valeur

le type de donnée est unique du fait de faire la récolte en shapefile.
Si il y a plus que un type de donnée, il faut faire des liens entre les différentes données

### Point

Peut être lié à des données de type surface. Dans ce cas là les infos montrées sont les valeurs des surfaces agrégées


### Section

### Valeur unique

Ceci regroupe toutes les données qui représente l'entiereté du bisse, où il n'est pas nécésaire d'avoir la résolution
plus précise par section ou même ponctuelle

### surface

Toutes les données qui ne représente pas seulement le cours d'eau en lui même. Cela pourrait être la surface des biotopes traversée, mais la données la plus importante est la demande en eau. On pourrait aussi ajouter les surfaces artificialisées qui deverse l'eau dans le bisse en cas de crue.

**N'a pas besoin d'être traité séparemment, le positionnement est fait à la main**
Dans le cas d'un lien vers une donnée de points:
Le résumé, ou autre calculs sont fait dans le clean du l'autre donnée

## Format des données

categorique: True
numerique: False

type_donnees est une liste: \
la liste colonne à traiter doit avoir le même nombre d'éléments

lien: "nom_indice"

### Lien

Ceci comporte les données vers lesquelles pointent d'autres données, par exemple les prises d'eau

Pas de traitement sur les données ni de plot, mais il faut snap les points

Pour les données qui renvooyent vers, il faut ajouter une ligne "lien" avec comme entrée une liste comportant
le nom de la couche et le nom de l'indice.

### Valeur numérique

Non: \
Entrée json: True/False

Plot: Bar chart avec la valeur, ou un line plot classique pour avoir une interpolation?
Si par section: on peut plot en escalier.

Cette donnée sera TOUJOURS appelée "val" dans QGIS

### Valeur catégorique

Non: \
Entrée json: True/False

Comme valeur numérique, mais si bar chart en point au lieu d'avoir la hauteur en valeur numérique
c'est le nombre d'occurence comptée. La couleur représente la valeur catégorique.

Cette donnée sera TOUJOURS appelée "type" dans QGIS

### Valeur catégorique + numérique

Il se peut qu'il ne faut pas seulement avoir une valeur catégorique ou numérique, mais d'avoir une valeur numérique
associé à une catégorie. Dans ce cas là il faut mettre les deux à True

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

## selection colonnes à traiter

json: "donees"

Pour autoriser de changer le nom des colonnes et de pouvoir avoir plusieurs indicateurs dans 1 seul shapefile, on peut préciser le nom des colonnes à traiter

Pour section: une liste avec les 2 colonnes, ou si une c'est la valeur du point avant ou après qui est compléter (en fonction de la direction de sampling)

Pour point: seulement une entree

## Visualisation

On sauvegarde:
- nom indice pour le titre
- type de donnée
- format
- file path + name



# Plan d'attaque

 - [x] Laisser les valeur temporelle de coté pour l'instant
 - [] Finish generic json
 - [] Update clavau.json with new format
 - [] adapt script to account for changes
 - [] create plots with plotly.express to display them in dash (make generic function)
 - [] link with dropdown menu and plot clavau data in dash

 - [] pywr