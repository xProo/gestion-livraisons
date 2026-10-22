"""Jeux de données : exemple du sujet et génération pour les mesures."""

import random

from src.colis import Colis

DESTINATIONS = (
    "Paris",
    "Lille",
    "Lyon",
    "Marseille",
    "Toulouse",
    "Nantes",
    "Strasbourg",
    "Bordeaux",
)

# Exemple fourni dans l'énoncé.
EXEMPLE_SUJET: tuple[Colis, ...] = (
    Colis(101, 8, 20, 2, "Paris"),
    Colis(102, 3, 10, 5, "Lille"),
    Colis(103, 12, 40, 1, "Lyon"),
    Colis(104, 5, 25, 4, "Paris"),
    Colis(105, 2, 15, 3, "Lille"),
)


def generer_colis(nombre: int, graine: int = 42) -> list[Colis]:
    """Crée ``nombre`` colis d'identifiants 1..nombre.

    Poids entre 1 et 30 kg, valeur entre 1 et 100, priorité entre 1 et 5.
    La graine fixe la série : les mesures du rapport sont reproductibles.

    Temps et espace : O(nombre).
    """
    if nombre < 0:
        raise ValueError("Le nombre de colis doit être positif ou nul.")
    alea = random.Random(graine)
    return [
        Colis(
            identifiant=indice,
            poids=alea.randint(1, 30),
            valeur=alea.randint(1, 100),
            priorite=alea.randint(1, 5),
            destination=alea.choice(DESTINATIONS),
        )
        for indice in range(1, nombre + 1)
    ]
