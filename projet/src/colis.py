"""Colis pris en charge par l'entreprise de livraison."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Colis:
    """Un colis identifié, avec son poids, sa valeur, sa priorité et sa destination.

    Hypothèse sur la priorité : un nombre plus grand signifie un colis plus
    important. Les exemples du sujet utilisent des priorités de 1 à 5, mais
    toute priorité entière supérieure ou égale à 1 est acceptée.
    """

    identifiant: int
    poids: int
    valeur: int
    priorite: int
    destination: str

    def __post_init__(self) -> None:
        if isinstance(self.identifiant, bool) or not isinstance(self.identifiant, int):
            raise ValueError("L'identifiant doit être un entier.")
        if isinstance(self.poids, bool) or not isinstance(self.poids, int):
            raise ValueError("Le poids doit être un entier.")
        if isinstance(self.valeur, bool) or not isinstance(self.valeur, int):
            raise ValueError("La valeur doit être un entier.")
        if isinstance(self.priorite, bool) or not isinstance(self.priorite, int):
            raise ValueError("La priorité doit être un entier.")
        if not isinstance(self.destination, str) or not self.destination.strip():
            raise ValueError("La destination est obligatoire.")
        if self.poids < 1:
            raise ValueError("Le poids doit être supérieur ou égal à 1 kg.")
        if self.valeur < 0:
            raise ValueError("La valeur doit être positive ou nulle.")
        if self.priorite < 1:
            raise ValueError("La priorité doit être supérieure ou égale à 1.")
        if self.destination != self.destination.strip():
            object.__setattr__(self, "destination", self.destination.strip())

    def score(self) -> int:
        """Score utilisé quand la priorité influence le chargement.

        score = valeur × priorité.

        La valeur reste le gain de base. La priorité agit comme multiplicateur :
        à valeur égale, un colis de priorité 5 compte cinq fois plus qu'un colis
        de priorité 1. Le poids n'entre pas dans le score : il reste la contrainte
        de capacité du camion.
        """
        return self.valeur * self.priorite


def creer_colis(
    identifiant: int,
    poids: int,
    valeur: int,
    priorite: int,
    destination: str,
) -> Colis:
    """Construit un colis après avoir nettoyé la destination."""
    if not isinstance(destination, str):
        raise ValueError("La destination doit être une chaîne de caractères.")
    return Colis(identifiant, poids, valeur, priorite, destination.strip())
