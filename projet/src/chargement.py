"""Sélection des colis à charger dans un camion de capacité limitée.

On résout un sac à dos 0/1 : chaque colis est pris au plus une fois, le poids
total ne dépasse pas la capacité, et l'on maximise un score entier.

Critères
---------
- ``valeur`` : on maximise la somme des valeurs.
- ``score`` : on maximise la somme des ``valeur × priorité``.

La seconde règle est celle qui fait intervenir la priorité. Elle ne maximise
pas la valeur monétaire : elle maximise un objectif qui rend les colis
prioritaires plus intéressants. Pour cet objectif, la programmation dynamique
et la rencontre au milieu sont optimales. Le glouton ne l'est pas.

Stratégie adaptative
--------------------
1. Programmation dynamique si n × (C + 1) reste sous un seuil.
   Temps O(n · C), espace O(n · C) pour mémoriser les décisions.
2. Sinon, rencontre au milieu si n est assez petit.
   Temps et espace O(2^(n/2) · n), indépendants de C. Optimale.
3. Sinon, glouton par densité score / poids.
   Temps O(n log n), espace O(n). La capacité est respectée, le score non
   garanti maximal.

Les poids et la capacité sont des entiers (des kilogrammes), comme dans
l'énoncé. C'est ce qui permet la programmation dynamique.
"""

from dataclasses import dataclass

from src.colis import Colis
from src.tri import tri_fusion

VALEUR = "valeur"
SCORE = "score"

# Environ 8 Mo pour la table de décisions, et un nombre de cases encore
# raisonnable à parcourir en Python.
SEUIL_CELLULES_DP = 8_000_000

# n = 36 découpe le problème en deux moitiés de 18 objets : 2^18 = 262 144 états.
SEUIL_RENCONTRE = 36

ALGO_DP = "programmation dynamique"
ALGO_RENCONTRE = "rencontre au milieu"
ALGO_GLOUTON = "glouton par densité"
ALGO_TRIVIAL = "cas trivial"


@dataclass(frozen=True, slots=True)
class ResultatChargement:
    """Plan de chargement produit par ``preparer_chargement``."""

    colis_choisis: tuple[Colis, ...]
    capacite: int
    critere: str
    algorithme: str
    optimal: bool
    explication: str

    @property
    def poids_total(self) -> int:
        return sum(colis.poids for colis in self.colis_choisis)

    @property
    def valeur_totale(self) -> int:
        return sum(colis.valeur for colis in self.colis_choisis)

    @property
    def score_total(self) -> int:
        return sum(colis.score() for colis in self.colis_choisis)

    @property
    def capacite_restante(self) -> int:
        return self.capacite - self.poids_total


def score_de(colis: Colis, critere: str) -> int:
    """Valeur numérique maximisée pour un colis, selon le critère choisi."""
    if critere == VALEUR:
        return colis.valeur
    if critere == SCORE:
        return colis.score()
    raise ValueError("Critère inconnu : utiliser 'valeur' ou 'score'.")


def preparer_chargement(
    colis: list[Colis] | tuple[Colis, ...],
    capacite: int,
    critere: str = SCORE,
) -> ResultatChargement:
    """Choisit un sous-ensemble de colis qui tient dans le camion.

    ``critere`` vaut ``valeur`` ou ``score``. Voir le docstring du module pour
    les complexités et la garantie d'optimalité.
    """
    if isinstance(capacite, bool) or not isinstance(capacite, int) or capacite < 0:
        raise ValueError("La capacité doit être un entier positif ou nul.")
    if critere not in (VALEUR, SCORE):
        raise ValueError("Critère inconnu : utiliser 'valeur' ou 'score'.")

    tous = list(colis)
    candidats = [element for element in tous if element.poids <= capacite]
    exclus = len(tous) - len(candidats)
    nombre = len(candidats)

    if capacite == 0 or nombre == 0:
        precision = "La capacité est nulle." if capacite == 0 else (
            "Aucun colis n'entre dans le camion."
        )
        if exclus:
            precision += f" {exclus} colis dépassent la capacité à eux seuls."
        return _resultat(
            [],
            capacite,
            critere,
            ALGO_TRIVIAL,
            True,
            precision + " La solution vide est optimale.",
        )

    cellules = nombre * (capacite + 1)
    if cellules <= SEUIL_CELLULES_DP:
        resultat = _programmation_dynamique(candidats, capacite, critere)
    elif nombre <= SEUIL_RENCONTRE:
        resultat = _rencontre_au_milieu(candidats, capacite, critere)
    else:
        resultat = _glouton(candidats, capacite, critere)

    if exclus:
        resultat = ResultatChargement(
            colis_choisis=resultat.colis_choisis,
            capacite=resultat.capacite,
            critere=resultat.critere,
            algorithme=resultat.algorithme,
            optimal=resultat.optimal,
            explication=(
                f"{resultat.explication} {exclus} colis plus lourds que le "
                "camion ont été écartés d'office : ils ne peuvent figurer dans "
                "aucune solution réalisable."
            ),
        )
    return resultat


def _resultat(
    choisis: list[Colis],
    capacite: int,
    critere: str,
    algorithme: str,
    optimal: bool,
    explication: str,
) -> ResultatChargement:
    poids = sum(colis.poids for colis in choisis)
    if poids > capacite:
        raise RuntimeError("Le chargement dépasse la capacité du camion.")
    return ResultatChargement(
        colis_choisis=tuple(choisis),
        capacite=capacite,
        critere=critere,
        algorithme=algorithme,
        optimal=optimal,
        explication=explication,
    )


def _programmation_dynamique(
    candidats: list[Colis],
    capacite: int,
    critere: str,
) -> ResultatChargement:
    """Sac à dos 0/1 itératif, avec reconstruction des colis retenus.

    ``dp[w]`` est le meilleur score atteignable avec une capacité exactement
    disponible de ``w`` kilogrammes, en n'utilisant que les colis déjà examinés.
    On parcourt les capacités à l'envers pour qu'un colis ne soit pris qu'une fois.

    La table ``pris`` retient, pour chaque colis et chaque capacité, si ce colis
    a été retenu pour améliorer cette capacité. Un octet par case suffit.
    """
    nombre = len(candidats)
    largeur = capacite + 1
    dp = [0] * largeur
    pris = bytearray(nombre * largeur)
    scores = [score_de(colis, critere) for colis in candidats]
    poids = [colis.poids for colis in candidats]

    for indice in range(nombre):
        masse = poids[indice]
        gain = scores[indice]
        base = indice * largeur
        for reste in range(capacite, masse - 1, -1):
            candidat = dp[reste - masse] + gain
            if candidat > dp[reste]:
                dp[reste] = candidat
                pris[base + reste] = 1

    reste = capacite
    choisis: list[Colis] = []
    for indice in range(nombre - 1, -1, -1):
        if pris[indice * largeur + reste]:
            choisis.append(candidats[indice])
            reste -= poids[indice]
    choisis.reverse()

    score = sum(score_de(colis, critere) for colis in choisis)
    if score != dp[capacite]:
        raise RuntimeError("La reconstruction du sac à dos est incohérente.")

    return _resultat(
        choisis,
        capacite,
        critere,
        ALGO_DP,
        True,
        (
            "Programmation dynamique du sac à dos 0/1. Chaque colis est pris "
            "au plus une fois. La solution est optimale pour le critère choisi."
        ),
    )


def _rencontre_au_milieu(
    candidats: list[Colis],
    capacite: int,
    critere: str,
) -> ResultatChargement:
    """Énumère les deux moitiés du lot puis combine les sous-ensembles compatibles.

    On trie la seconde moitié par poids et l'on précalcule le meilleur score
    atteignable avec un poids inférieur ou égal à chaque préfixe. Pour chaque
    sous-ensemble de la première moitié, une dichotomie trouve le complément
    le plus intéressant qui tient encore dans le camion.
    """
    milieu = len(candidats) // 2
    gauche = candidats[:milieu]
    droite = candidats[milieu:]
    scores = [score_de(colis, critere) for colis in candidats]
    scores_gauche = scores[:milieu]
    scores_droite = scores[milieu:]

    etats_gauche = _enumerer(gauche, scores_gauche)
    etats_droite = _enumerer(droite, scores_droite)
    etats_droite = tri_fusion(etats_droite, lambda etat: etat[0])

    meilleur_score: list[int] = []
    meilleur_masque: list[int] = []
    courant = -1
    masque_courant = 0
    for _poids, gain, masque in etats_droite:
        if gain > courant:
            courant = gain
            masque_courant = masque
        meilleur_score.append(courant)
        meilleur_masque.append(masque_courant)
    poids_droite = [etat[0] for etat in etats_droite]

    meilleur = -1
    masque_gauche_retenu = 0
    masque_droite_retenu = 0
    for masse, gain, masque in etats_gauche:
        if masse > capacite:
            continue
        indice = _dernier_indice_au_plus(poids_droite, capacite - masse)
        total = gain
        masque_complement = 0
        if indice >= 0:
            total += meilleur_score[indice]
            masque_complement = meilleur_masque[indice]
        if total > meilleur:
            meilleur = total
            masque_gauche_retenu = masque
            masque_droite_retenu = masque_complement

    choisis = _decoder(gauche, masque_gauche_retenu)
    choisis.extend(_decoder(droite, masque_droite_retenu))
    return _resultat(
        choisis,
        capacite,
        critere,
        ALGO_RENCONTRE,
        True,
        (
            "Rencontre au milieu : les sous-ensembles des deux moitiés sont "
            "énumérés puis combinés par dichotomie. La solution est optimale "
            "pour le critère choisi. Le coût dépend de n, pas de la capacité."
        ),
    )


def _enumerer(colis: list[Colis], scores: list[int]) -> list[tuple[int, int, int]]:
    """Tous les sous-ensembles : (poids, score, masque de bits)."""
    etats = [(0, 0, 0)]
    for indice, element in enumerate(colis):
        bit = 1 << indice
        masse = element.poids
        gain = scores[indice]
        # Liste calculée d'abord : étendre pendant le parcours relancerait l'itération.
        ajouts = [
            (poids + masse, score + gain, masque | bit) for poids, score, masque in etats
        ]
        etats.extend(ajouts)
    return etats


def _decoder(colis: list[Colis], masque: int) -> list[Colis]:
    return [element for indice, element in enumerate(colis) if masque & (1 << indice)]


def _dernier_indice_au_plus(poids_tries: list[int], limite: int) -> int:
    """Plus grand indice dont le poids est inférieur ou égal à ``limite``, ou -1.

    Dichotomie. Temps O(log m) où m est le nombre de sous-ensembles.
    """
    gauche = 0
    droite = len(poids_tries) - 1
    reponse = -1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        if poids_tries[milieu] <= limite:
            reponse = milieu
            gauche = milieu + 1
        else:
            droite = milieu - 1
    return reponse


def _glouton(
    candidats: list[Colis],
    capacite: int,
    critere: str,
) -> ResultatChargement:
    """Prend les colis dans l'ordre décroissant de la densité score / poids.

    Ce tri réutilise le tri fusion du projet. En cas d'égalité de densité,
    l'ordre d'origine est conservé. Un colis est chargé s'il tient dans la
    place restante. Rien ne garantit que le score total soit maximal.
    """
    tries = tri_fusion(
        candidats,
        lambda colis: -(score_de(colis, critere) / colis.poids),
    )
    choisis: list[Colis] = []
    reste = capacite
    for colis in tries:
        if colis.poids <= reste:
            choisis.append(colis)
            reste -= colis.poids

    return _resultat(
        choisis,
        capacite,
        critere,
        ALGO_GLOUTON,
        False,
        (
            "Glouton par densité (score / poids), trié par le tri fusion. "
            "La capacité est respectée, mais le score n'est pas toujours maximal. "
            "La programmation dynamique aurait demandé trop de cases, et il y a "
            f"plus de {SEUIL_RENCONTRE} colis pour une rencontre au milieu."
        ),
    )
