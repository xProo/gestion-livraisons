"""Stats en un seul parcours. O(n)."""

from src.collection import CollectionColis


def calculer(collection: CollectionColis) -> dict:
    """Stats de la collection. Effectifs vides s'il n'y a aucun colis."""
    nombre = 0
    poids_total = 0
    valeur_totale = 0
    priorite_totale = 0
    poids_min = None
    poids_max = None
    valeur_min = None
    valeur_max = None
    par_destination: dict[str, int] = {}
    par_priorite: dict[int, int] = {}

    for colis in collection:
        nombre += 1
        poids_total += colis.poids
        valeur_totale += colis.valeur
        priorite_totale += colis.priorite
        poids_min = colis.poids if poids_min is None else min(poids_min, colis.poids)
        poids_max = colis.poids if poids_max is None else max(poids_max, colis.poids)
        valeur_min = colis.valeur if valeur_min is None else min(valeur_min, colis.valeur)
        valeur_max = colis.valeur if valeur_max is None else max(valeur_max, colis.valeur)
        par_destination[colis.destination] = par_destination.get(colis.destination, 0) + 1
        par_priorite[colis.priorite] = par_priorite.get(colis.priorite, 0) + 1

    moyenne = (priorite_totale / nombre) if nombre else None
    return {
        "nombre": nombre,
        "poids_total": poids_total,
        "valeur_totale": valeur_totale,
        "priorite_moyenne": moyenne,
        "poids_min": poids_min,
        "poids_max": poids_max,
        "valeur_min": valeur_min,
        "valeur_max": valeur_max,
        "par_destination": par_destination,
        "par_priorite": par_priorite,
    }
