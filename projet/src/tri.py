"""Tri fusion ascendant, stable. O(n log n) temps, O(n) mémoire."""

from typing import Callable, TypeVar

T = TypeVar("T")


def tri_fusion(elements: list[T], cle: Callable[[T], object]) -> list[T]:
    """Nouvelle liste triée selon cle. L'entrée n'est pas modifiée.

    Bottom-up, clés calculées une seule fois.
    O(n log n) dans tous les cas, O(n) en mémoire, pas de récursion.
    Stable : à clé égale, on garde l'ordre de départ.
    """
    source = list(elements)
    nombre = len(source)
    if nombre <= 1:
        return source

    cles_source = [cle(element) for element in source]
    tampon = source[:]
    cles_tampon = cles_source[:]

    taille = 1
    lire_source = True
    while taille < nombre:
        if lire_source:
            _passer(source, cles_source, tampon, cles_tampon, nombre, taille)
        else:
            _passer(tampon, cles_tampon, source, cles_source, nombre, taille)
        lire_source = not lire_source
        taille *= 2

    # le résultat est dans le tableau qu'on vient d'écrire
    if lire_source:
        return source
    return tampon


def _passer(
    lecture: list,
    cles_lecture: list,
    ecriture: list,
    cles_ecriture: list,
    nombre: int,
    taille: int,
) -> None:
    debut = 0
    while debut < nombre:
        milieu = min(debut + taille, nombre)
        fin = min(debut + 2 * taille, nombre)
        _fusionner(
            lecture,
            cles_lecture,
            ecriture,
            cles_ecriture,
            debut,
            milieu,
            fin,
        )
        debut += 2 * taille


def _fusionner(
    lecture: list,
    cles_lecture: list,
    ecriture: list,
    cles_ecriture: list,
    debut: int,
    milieu: int,
    fin: int,
) -> None:
    """Fusionne deux moitiés déjà triées."""
    gauche = debut
    droite = milieu
    position = debut
    while gauche < milieu and droite < fin:
        # < strict : en cas d'égalité on garde la gauche
        if cles_lecture[droite] < cles_lecture[gauche]:
            ecriture[position] = lecture[droite]
            cles_ecriture[position] = cles_lecture[droite]
            droite += 1
        else:
            ecriture[position] = lecture[gauche]
            cles_ecriture[position] = cles_lecture[gauche]
            gauche += 1
        position += 1

    while gauche < milieu:
        ecriture[position] = lecture[gauche]
        cles_ecriture[position] = cles_lecture[gauche]
        gauche += 1
        position += 1

    while droite < fin:
        ecriture[position] = lecture[droite]
        cles_ecriture[position] = cles_lecture[droite]
        droite += 1
        position += 1
