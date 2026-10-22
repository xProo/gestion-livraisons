"""Représentation d'un colis."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Colis:
    """Id, poids (kg), valeur, priorité, destination.

    Priorité >= 1 : plus le nombre est grand, plus le colis est important.
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
        """valeur × priorité. Le poids n'entre pas dans le score."""
        return self.valeur * self.priorite


def creer_colis(
    identifiant: int,
    poids: int,
    valeur: int,
    priorite: int,
    destination: str,
) -> Colis:
    """Crée un colis, destination sans espaces autour."""
    if not isinstance(destination, str):
        raise ValueError("La destination doit être une chaîne de caractères.")
    return Colis(identifiant, poids, valeur, priorite, destination.strip())
