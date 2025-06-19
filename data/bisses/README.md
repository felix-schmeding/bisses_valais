# Données

Dans la pipeline actuelle, il faut:

1. Créer un fichier .shp sur QGIS, avec comme entrées:
    - Points: "Type" avec une valeur catégorique (ex: Panneaux didactiques)
    - Sections: "val_av" et "val_ap" avec une valeur catégorique (ex: revêtement)
    - Surfaces: "link_id" et "type"+"besoin" (ex: prises_eau et surfaces irriguées)
2. Ajouter ce fichier dans le .json du bisses: 
    - si cette donnée n'existe pas encore dans le fichier "data/_template/donnees.json", completer avec les paramètres correspondants
    - dans l'entrée de la liste correspondante
    - avec le même identifiant que dans le fichier donnees.json (pour l'instant seulement le chemin de sauvegarde)
3. Run toutes les cellules du fichier data.ipynb
4. Run visualisation.ipynb

Pour l'instant les paramètres utilisés dans le fichier donnees.json sont:
- nom_indice
- type_donnee
- col: seulement pour le type surface

Le fichier donnees.json a été structuré dans le but d'automatiser le traitement des données en fonction des types de données. Il suffit seulement de donner le type, les noms des colonnes ect et le reste est fait par le programme.

- "type_donnee": section, point, etc. Ce que représentent les données
- "format_donnee": numérique, catégorique, ect. Est une liste, si jamais une entrée posède plusieurs valeurs disctinctes (pas implémenté)
- "drop_down": QGIS permet de charger les valeurs qui sont selectionnable pour une entrée catégorique. (pas implémenté mais permettrais de vérifier si les entreées sont conformes)
- "col": liste de liste des noms des colonnes qui contiennent les valeurs. Il faut deux colonnes pour le type "section". Seulement implémenter pour les surfaces.

## Prochaines étapes

1. Adapter le code pour que touts les paramètres de donnees.json soient vraiment pris en compte
2. Implémenter le code pour les données de type numérique (traitement + visualisation)
3. Si nécéssaire, le type "lien" est seulement fait pour les prises d'eau liées aux surface. Il mérite d'être adapté pour pouvoir être appliqué à d'autres données (le point 1. s'applique aussi au traitement des données "lien")