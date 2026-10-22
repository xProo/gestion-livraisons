"""Colis indexés par identifiant (dict).

Ajout et recherche : O(1) en moyenne.
Parcours : O(n). Tri à la demande : O(n log n), O(n) en mémoire.
"""

from src.colis import Colis
from src.tri import tri_fusion


class IdentifiantDejaPresent(ValueError):
    """Cet identifiant est déjà utilisé."""


class CollectionColis:
    """Colis avec identifiant unique."""

    def __init__(self) -> None:
        self._par_id: dict[int, Colis] = {}

    def __len__(self) -> int:
        return len(self._par_id)

    def __iter__(self):
        return iter(self._par_id.values())

    def ajouter(self, colis: Colis) -> None:
        """Ajoute un colis. Erreur si l'identifiant existe déjà. O(1) en moyenne."""
        if colis.identifiant in self._par_id:
            raise IdentifiantDejaPresent(
                f"Le colis {colis.identifiant} existe déjà."
            )
        self._par_id[colis.identifiant] = colis

    def rechercher(self, identifiant: int) -> Colis | None:
        """Colis correspondant à l'identifiant, ou None. O(1) en moyenne."""
        return self._par_id.get(identifiant)

    def tous(self) -> list[Colis]:
        """Colis dans l'ordre d'insertion. O(n)."""
        return list(self._par_id.values())

    def selon_poids(self, decroissant: bool = False) -> list[Colis]:
        """Tri par poids."""
        return self._selon(lambda colis: colis.poids, decroissant)

    def selon_valeur(self, decroissant: bool = False) -> list[Colis]:
        """Tri par valeur."""
        return self._selon(lambda colis: colis.valeur, decroissant)

    def selon_priorite(self, decroissant: bool = False) -> list[Colis]:
        """Tri par priorité."""
        return self._selon(lambda colis: colis.priorite, decroissant)

    def _selon(self, cle, decroissant: bool) -> list[Colis]:
        if decroissant:
            # clé négative pour l'ordre décroissant
            return tri_fusion(self.tous(), lambda colis: -cle(colis))
        return tri_fusion(self.tous(), cle)


def depuis_liste(colis: list[Colis]) -> CollectionColis:
    """Construit la collection. Erreur si un identifiant est en double."""
    collection = CollectionColis()
    for element in colis:
        collection.ajouter(element)
    return collection
