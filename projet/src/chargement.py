"""Choix des colis à mettre dans le camion (sac à dos 0/1).

Critère "valeur" : somme des valeurs.
Critère "score" : somme de valeur × priorité.

- programmation dynamique si n × (C + 1) <= seuil (O(n·C))
- sinon rencontre au milieu si n <= 36 (O(2^(n/2)))
- sinon glouton par densité, pas toujours optimal (O(n log n))
"""

from dataclasses import dataclass

from src.colis import Colis
from src.tri import tri_fusion

VALEUR = "valeur"
SCORE = "score"

# au-delà, la table est trop grosse (environ 8 Mo)
SEUIL_CELLULES_DP = 8_000_000

# moitié de 18 objets : 2^18 états
SEUIL_RENCONTRE = 36

ALGO_DP = "programmation dynamique"
ALGO_RENCONTRE = "rencontre au milieu"
ALGO_GLOUTON = "glouton par densité"
ALGO_TRIVIAL = "cas trivial"


@dataclass(frozen=True, slots=True)
class ResultatChargement:
    """Résultat de preparer_chargement."""

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
    """Valeur ou score du colis, selon le critère."""
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
    """Sous-ensemble de colis qui tient dans le camion.

    critere vaut "valeur" ou "score".
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
                "camion ont été écartés."
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
    """Sac à dos 0/1. dp[w] = meilleur score avec une capacité w.

    Parcours des capacités à l'envers pour ne prendre chaque colis qu'une fois.
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
            "Programmation dynamique (sac à dos 0/1). "
            "Solution optimale pour le critère choisi."
        ),
    )


def _rencontre_au_milieu(
    candidats: list[Colis],
    capacite: int,
    critere: str,
) -> ResultatChargement:
    """Coupe le lot en deux, énumère chaque moitié, combine par dichotomie."""
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
            "Rencontre au milieu. Solution optimale pour le critère choisi. "
            "Le temps dépend de n, pas de la capacité."
        ),
    )


def _enumerer(colis: list[Colis], scores: list[int]) -> list[tuple[int, int, int]]:
    """Tous les sous-ensembles : (poids, score, masque)."""
    etats = [(0, 0, 0)]
    for indice, element in enumerate(colis):
        bit = 1 << indice
        masse = element.poids
        gain = scores[indice]
        # liste à part, sinon le extend relance la boucle
        ajouts = [
            (poids + masse, score + gain, masque | bit) for poids, score, masque in etats
        ]
        etats.extend(ajouts)
    return etats


def _decoder(colis: list[Colis], masque: int) -> list[Colis]:
    return [element for indice, element in enumerate(colis) if masque & (1 << indice)]


def _dernier_indice_au_plus(poids_tries: list[int], limite: int) -> int:
    """Plus grand indice de poids <= limite, ou -1. Dichotomie."""
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
    """Colis pris par densité décroissante, tant qu'il reste de la place.

    Pas toujours optimal.
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
            "Glouton par densité (score / poids). "
            "La capacité est respectée, le score n'est pas toujours maximal."
        ),
    )
