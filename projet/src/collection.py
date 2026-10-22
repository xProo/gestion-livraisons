"""Collection de colis indexée par identifiant.

Stratégie : table de hachage (``dict`` de CPython).

- ajout : O(1) en moyenne, amorti
- recherche par identifiant : O(1) en moyenne
- parcours de tous les colis : O(n)
- affichage trié : O(n log n) temps et O(n) espace, via le tri fusion

Espace total : O(n).

Les vues triées sont calculées à la demande. On ne maintient pas trois index
triés en permanence : les afficher coûte déjà O(n), et un tri O(n log n) reste
adapté jusqu'à 100 000 colis (voir les mesures du rapport).
"""

from src.colis import Colis
from src.tri import tri_fusion


class IdentifiantDejaPresent(ValueError):
    """L'identifiant demandé est déjà associé à un colis."""


class CollectionColis:
    """Ensemble de colis dont l'identifiant est unique."""

    def __init__(self) -> None:
        self._par_id: dict[int, Colis] = {}

    def __len__(self) -> int:
        return len(self._par_id)

    def __iter__(self):
        return iter(self._par_id.values())

    def ajouter(self, colis: Colis) -> None:
        """Ajoute un colis. Refuse un identifiant déjà présent.

        Temps moyen : O(1). Espace : O(1) en plus de l'objet stocké.
        """
        if colis.identifiant in self._par_id:
            raise IdentifiantDejaPresent(
                f"Le colis {colis.identifiant} existe déjà."
            )
        self._par_id[colis.identifiant] = colis

    def rechercher(self, identifiant: int) -> Colis | None:
        """Retrouve un colis par son identifiant, ou ``None``.

        Temps moyen : O(1). Espace supplémentaire : O(1).
        """
        return self._par_id.get(identifiant)

    def tous(self) -> list[Colis]:
        """Colis dans l'ordre d'insertion. Temps et espace : O(n)."""
        return list(self._par_id.values())

    def selon_poids(self, decroissant: bool = False) -> list[Colis]:
        """Colis triés par poids. Temps O(n log n), espace O(n)."""
        return self._selon(lambda colis: colis.poids, decroissant)

    def selon_valeur(self, decroissant: bool = False) -> list[Colis]:
        """Colis triés par valeur. Temps O(n log n), espace O(n)."""
        return self._selon(lambda colis: colis.valeur, decroissant)

    def selon_priorite(self, decroissant: bool = False) -> list[Colis]:
        """Colis triés par priorité. Temps O(n log n), espace O(n)."""
        return self._selon(lambda colis: colis.priorite, decroissant)

    def _selon(self, cle, decroissant: bool) -> list[Colis]:
        if decroissant:
            # Le tri reste stable : à critère égal, l'ordre d'insertion est gardé.
            return tri_fusion(self.tous(), lambda colis: -cle(colis))
        return tri_fusion(self.tous(), cle)


def depuis_liste(colis: list[Colis]) -> CollectionColis:
    """Construit une collection. Lève une erreur si un identifiant est répété."""
    collection = CollectionColis()
    for element in colis:
        collection.ajouter(element)
    return collection
