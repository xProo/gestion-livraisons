"""Tri fusion ascendant, stable, de complexité garantie.

Le tri est écrit explicitement : l'affichage ordonné des colis est un cœur
algorithmique du projet, il ne délègue donc pas à la fonction native ``sorted``.
"""

from typing import Callable, TypeVar

T = TypeVar("T")


def tri_fusion(elements: list[T], cle: Callable[[T], object]) -> list[T]:
    """Retourne une nouvelle liste triée selon ``cle``, sans modifier l'entrée.

    Algorithme : tri fusion ascendant (bottom-up). Les clés sont calculées une
    seule fois, puis chaque passe fusionne des sous-suites de taille 1, 2, 4…

    Temps : O(n log n) dans tous les cas. La fonction ``cle`` est appelée n fois.
    Espace : O(n) pour la copie, le tableau tampon et les clés. Pas de pile
    récursive : l'espace supplémentaire de la récursion est O(1).
    Stabilité : si deux clés sont égales, l'élément le plus à gauche reste
    devant. L'ordre d'insertion des colis est donc conservé en cas d'ex æquo.
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

    # Après une passe, le résultat se trouve dans le tableau qui vient d'être écrit.
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
    """Fusionne lecture[debut:milieu] et lecture[milieu:fin], déjà triées."""
    gauche = debut
    droite = milieu
    position = debut
    while gauche < milieu and droite < fin:
        # Comparaison stricte : en cas d'égalité, on prend la moitié gauche.
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
