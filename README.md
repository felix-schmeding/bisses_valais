# bisses_valais
Developpement d'un modèle conceptuel pour les bisses valaisans

# Environnement python

Les librairies principales nécéssaires sont:
- numpy
- pandas
- geopandas
- dash
- plotly
- matplotlib
- jupyter

Pour la simplicité, en utilisant miniconda sur windows, il suffit d'éxeuter la ligne suivante dans le terminal:

```conda env create -f bisses.yml```

# Données

veuillez extraire le fichier .zip téléchargeable ici:

https://drive.google.com/file/d/1ekxOOZdapU4JCK8PRz-tVJuAGe8tSaQP/view?usp=sharing

Le fichier .qgz et le dossier /data doivent être placés dans le dossier principale de ce projet.

Pour pouvoir traiter les données, il suffit de suivre les étapes suivantes:
- Dans QGIS: dupliquer une couche template du format de donnée adaptée
- modifier le json propre au bisse en ajouter un dict avec comme "key" la même que dans le json donnees.json (/template)
- ajouter les infos supplémentaire (date, chemin de sauvegarde, ...)

Pour plus de détail, voir le README.md dans le dossier "data/bisses"



# Guide d'utilisation QGIS:

## Download DEM

Download extention: “Swiss geo downloader”

Go to “Web→Swiss Geo downloader”

Search for swissALTI3D

Select the bisse from dataset.

On the identify result on the right, right click on the bisse.

Select zoom to feature

In extend, click map canvas extend

If want to reduce size of download, deselect images where bisse is not going through

in 3. Files, click request file list. select 0.5 resolution

Download to project/data/DEM and extract

## Ajout couches agriculture

### a) **Valve Layer:**

Add a field called something like `valve_id` (type: text or integer). Make sure each valve has a **unique** ID. This can also just be the ID

### b) **Irrigated Areas Layer:**

Add a field called `valve_id` too — this will act as a **foreign key** to the valve it's linked to.

This lets you **link multiple polygons to a single valve**.

### **3. Optional: Use Attribute Form Relations**

To make data entry easier, you can set up a **relation** between valves and irrigated areas:

### a) Go to:

`Project` > `Properties` > `Relations`

### b) Add a new relation:

- **Name**: e.g., "Valve to Fields"
- **Referencing Layer**: Your **irrigated areas**
- **Referenced Layer**: Your **valves**
- **Field on referencing layer**: `valve_id` (in irrigated areas)
- **Field on referenced layer**: `valve_id` (in valves)
- Check **"Provide a form for adding related features" (NOT POSSIBLE)**

Now, when you open the attribute form of a valve, you'll see (and can edit) all the related irrigated areas.

## View and edit:

https://docs.qgis.org/3.40/en/docs/user_manual/working_with_vector/joins_relations.html
The relations will appear in the info field of the valves, where all irrigation fields will be shown

They can be modified from here.

### Proposed workflow:

1. create both layers
2. get field data:
    1. position valves as points when in the field
    2. go talk to farmers and know what area is irrigated with what valve, what grow on it etc
3. Manually add irrigation data: can do it straight from valves attribute dialog
4. You can easily see on QGIS which field goes to which valve
5. In python combine all water needs of the valve together
6. run hecras with outflow


## Field type

Do this if imported the new template layer

### Multiselection menu

right click layer→ properties → Attribute forms

Select field→ Widjet type to Value map 

Load data from csv file→ apply→ok

### Add picture as attachement

1. add new field as text
2. Widget type→ attachment
3. store path as: relative to project



## Unique ID field

Properties→ attributes form

default expressions:

`CASE
WHEN maximum("id") is NULL THEN 0
WHEN "id" is NULL THEN maximum("id")+1
ELSE "id"
END`

## Download DEM

Download extention: “Swiss geo downloader”

Go to “Web→Swiss Geo downloader”

Search for swissALTI3D

Select the bisse from dataset.

On the identify result on the right, right click on the bisse.

Select zoom to feature

In extend, click map canvas extend

If want to reduce size of download, deselect images where bisse is not going through

in 3. Files, click request file list. select 0.5 resolution

Download to project/data/DEM and extract



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

