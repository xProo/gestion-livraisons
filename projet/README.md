# Gestion des livraisons

Programme de gestion des colis et de préparation du chargement d'un camion.

Le langage retenu est **Python 3** (3.10 ou plus récent). Il est indiqué ici, comme demandé, et justifié plus longuement dans `rapport.pdf`. En bref : le `dict` fournit la table de hachage utilisée pour retrouver un colis, et le langage ne donne aucun avantage à l'évaluation. Le tri et le sac à dos, qui sont le cœur algorithmique du devoir, sont écrits dans le projet. Aucune bibliothèque externe ne résout ces problèmes. Seule la bibliothèque standard est utilisée (menu, mesures de temps, génération aléatoire).

## Lancer le programme

Depuis ce dossier :

```text
python -m src
```

Les tests et les mesures :

```text
python -m unittest discover -s tests -v
python -m src.benchmark
```

## Menu

```text
===== GESTION DES LIVRAISONS =====
1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Charger des données
9. Mesurer les performances
0. Quitter
```

L'entrée 8 charge l'exemple du sujet (5 colis) ou génère 100, 1 000, 10 000 ou 100 000 colis. L'affichage est paginé : au-delà de 20 lignes, le programme demande s'il faut continuer. Les mesures de l'entrée 9 n'effacent pas la collection en cours.

## Données

Chaque colis a un identifiant, un poids en kilogrammes (entier ≥ 1), une valeur (entier ≥ 0), une priorité (entier ≥ 1) et une destination. L'identifiant est unique.

Hypothèse sur la priorité : **un nombre plus grand est plus important**. Les exemples du sujet utilisent 1 à 5, mais toute priorité ≥ 1 est acceptée.

## Algorithmes

Le détail, les complexités et les mesures sont dans `rapport.pdf`. Résumé :

| Besoin | Algorithme | Temps | Espace |
| --- | --- | --- | --- |
| Retrouver un colis | Table de hachage (`dict`) | O(1) en moyenne | O(n) |
| Trier par poids, valeur ou priorité | Tri fusion ascendant, stable | O(n log n) | O(n) |
| Charger le camion | Sac à dos 0/1 | voir ci-dessous | voir ci-dessous |

Le chargement maximise soit la valeur, soit le score `valeur × priorité`. Trois méthodes sont utilisées selon la taille :

1. **Programmation dynamique**, si `n × (capacité + 1) ≤ 8 000 000`. Optimale pour le critère choisi. Temps O(n · C), espace O(n · C).
2. **Rencontre au milieu**, si la table dynamique est trop grande et que `n ≤ 36`. Optimale aussi. Le coût dépend de n, pas de la capacité.
3. **Glouton par densité** (score / poids) sinon. La capacité est respectée, le score n'est pas toujours maximal. Le menu l'indique.

Avec les 100 000 colis demandés et un camion de 50 kg, c'est la programmation dynamique qui s'exécute.

## Arborescence

```text
projet/
├── src/
│   ├── colis.py            colis et score valeur × priorité
│   ├── collection.py       table de hachage et vues triées
│   ├── tri.py              tri fusion
│   ├── chargement.py       sac à dos
│   ├── statistiques.py
│   ├── donnees.py          exemple du sujet et générateur
│   ├── benchmark.py        mesures 100 à 100 000
│   ├── interface.py        menu
│   └── __main__.py
├── tests/
│   └── test_algorithmes.py
├── README.md
└── rapport.pdf
```
