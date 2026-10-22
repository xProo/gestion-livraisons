"""Mesures pour 100, 1 000, 10 000 et 100 000 colis (graine 42).

Lancer depuis le dossier projet : python -m src.benchmark
"""

import argparse
import json
import time
import tracemalloc
from dataclasses import asdict, dataclass

from src.chargement import preparer_chargement
from src.collection import depuis_liste
from src.donnees import generer_colis
from src.tri import tri_fusion

CAPACITE_MESURE = 50
NOMBRE_RECHERCHES = 5_000


@dataclass
class Mesure:
    nombre: int
    ajout_ms: float
    recherche_us: float
    tri_fusion_ms: float
    tri_natif_ms: float
    chargement_ms: float
    algorithme_chargement: str
    memoire_tri_ko: float
    memoire_chargement_ko: float


def executer(
    tailles: tuple[int, ...] = (100, 1_000, 10_000, 100_000),
    capacite: int = CAPACITE_MESURE,
    recherches: int = NOMBRE_RECHERCHES,
    graine: int = 42,
) -> list[Mesure]:
    """Ajout, recherche, tri et chargement pour chaque taille."""
    return [
        _mesurer_taille(nombre, capacite, recherches, graine) for nombre in tailles
    ]


def afficher(mesures: list[Mesure]) -> None:
    """Affiche le tableau des mesures."""
    print("Mesures reproductibles (graine 42, capacité du camion = 50 kg).")
    print("La recherche est une moyenne sur plusieurs identifiants présents et absents.")
    print()
    entete = (
        f"{'n':>8} {'ajout ms':>10} {'rech. µs':>10} "
        f"{'tri ms':>10} {'natif ms':>10} {'camion ms':>10} "
        f"{'algo':<24} {'tri Ko':>10} {'camion Ko':>10}"
    )
    print(entete)
    print("-" * len(entete))
    for mesure in mesures:
        print(
            f"{mesure.nombre:8d} {mesure.ajout_ms:10.2f} {mesure.recherche_us:10.3f} "
            f"{mesure.tri_fusion_ms:10.2f} {mesure.tri_natif_ms:10.2f} "
            f"{mesure.chargement_ms:10.2f} {mesure.algorithme_chargement:<24} "
            f"{mesure.memoire_tri_ko:10.1f} {mesure.memoire_chargement_ko:10.1f}"
        )


def _mesurer_taille(nombre: int, capacite: int, recherches: int, graine: int) -> Mesure:
    colis = generer_colis(nombre, graine)

    debut = time.perf_counter()
    collection = depuis_liste(colis)
    ajout_ms = (time.perf_counter() - debut) * 1_000

    recherche_us = _mesurer_recherches(collection, nombre, recherches)
    tri_fusion_ms = _chrono(lambda: collection.selon_poids())
    tri_natif_ms = _chrono(lambda: sorted(colis, key=lambda element: element.poids))

    def charger():
        return preparer_chargement(colis, capacite, critere="score")

    debut = time.perf_counter()
    resultat = charger()
    chargement_ms = (time.perf_counter() - debut) * 1_000

    # vérif hors chrono
    tries = collection.selon_poids()
    if any(tries[i].poids > tries[i + 1].poids for i in range(len(tries) - 1)):
        raise RuntimeError("Le tri fusion n'est pas ordonné.")

    return Mesure(
        nombre=nombre,
        ajout_ms=ajout_ms,
        recherche_us=recherche_us,
        tri_fusion_ms=tri_fusion_ms,
        tri_natif_ms=tri_natif_ms,
        chargement_ms=chargement_ms,
        algorithme_chargement=resultat.algorithme,
        memoire_tri_ko=_pic_ko(lambda: tri_fusion(colis, lambda element: element.poids)),
        memoire_chargement_ko=_pic_ko(charger),
    )


def _mesurer_recherches(collection, nombre: int, recherches: int) -> float:
    """Temps moyen d'une recherche, en µs.

    Une requête sur deux cherche un id absent.
    """
    debut = time.perf_counter()
    for indice in range(recherches):
        if indice % 2 == 0:
            collection.rechercher((indice % nombre) + 1)
        else:
            collection.rechercher(-(indice + 1))
    ecoule = time.perf_counter() - debut
    return (ecoule / recherches) * 1_000_000


def _chrono(action) -> float:
    debut = time.perf_counter()
    action()
    return (time.perf_counter() - debut) * 1_000


def _pic_ko(action) -> float:
    """Pic mémoire en Ko. À part du chrono, tracemalloc ralentit."""
    tracemalloc.start()
    action()
    _courant, pic = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return pic / 1024


def main() -> None:
    analyseur = argparse.ArgumentParser(description="Mesures de performance du projet.")
    analyseur.add_argument(
        "--json",
        help="Chemin d'un fichier JSON où écrire les mesures.",
    )
    arguments = analyseur.parse_args()
    mesures = executer()
    afficher(mesures)
    if arguments.json:
        with open(arguments.json, "w", encoding="utf-8") as fichier:
            json.dump([asdict(mesure) for mesure in mesures], fichier, indent=2)
            fichier.write("\n")


if __name__ == "__main__":
    main()
