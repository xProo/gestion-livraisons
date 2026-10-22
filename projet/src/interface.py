"""Menu en ligne de commande."""

import time

from src.chargement import SCORE, VALEUR, ResultatChargement, preparer_chargement
from src.colis import Colis, creer_colis
from src.collection import CollectionColis, IdentifiantDejaPresent, depuis_liste
from src.donnees import EXEMPLE_SUJET, generer_colis
from src.statistiques import calculer

PAGE = 20

CRITERES = {
    "1": (VALEUR, "valeur monétaire"),
    "2": (SCORE, "score valeur × priorité"),
}


class Session:
    """Collection en cours et dernier chargement."""

    def __init__(self) -> None:
        self.collection = CollectionColis()
        self.chargement: ResultatChargement | None = None


def boucle() -> None:
    """Boucle du menu jusqu'au choix 0."""
    session = Session()
    actions = {
        "1": afficher_colis,
        "2": ajouter_colis,
        "3": rechercher_colis,
        "4": organiser_colis,
        "5": preparer_camion,
        "6": afficher_chargement,
        "7": afficher_statistiques,
        "8": charger_donnees,
        "9": mesurer,
    }
    while True:
        _afficher_menu(session)
        choix = _lire_ligne("Choix : ")
        if choix == "0":
            print("Au revoir.")
            return
        action = actions.get(choix)
        if action is None:
            print("Choix invalide.")
            continue
        action(session)


def afficher_colis(session: Session) -> None:
    """Liste les colis dans l'ordre d'insertion."""
    _paginer(session.collection.tous(), "Colis dans l'ordre d'insertion")


def ajouter_colis(session: Session) -> None:
    """Saisie d'un colis, puis ajout."""
    try:
        colis = creer_colis(
            _lire_entier("Identifiant : "),
            _lire_entier("Poids (kg) : ", minimum=1),
            _lire_entier("Valeur : ", minimum=0),
            _lire_entier("Priorité (>= 1, plus grand = plus important) : ", minimum=1),
            _lire_texte("Destination : "),
        )
        session.collection.ajouter(colis)
    except (ValueError, IdentifiantDejaPresent) as erreur:
        print(erreur)
        return
    print(f"Colis {colis.identifiant} ajouté.")


def rechercher_colis(session: Session) -> None:
    """Recherche par identifiant."""
    identifiant = _lire_entier("Identifiant recherché : ")
    debut = time.perf_counter()
    colis = session.collection.rechercher(identifiant)
    duree = (time.perf_counter() - debut) * 1_000_000
    if colis is None:
        print(f"Aucun colis avec l'identifiant {identifiant}.")
    else:
        _entete()
        print(_ligne(colis))
    print(f"Recherche terminée en {duree:.1f} µs.")


def organiser_colis(session: Session) -> None:
    """Tri par poids, valeur ou priorité."""
    print()
    print("1. Poids croissant")
    print("2. Poids décroissant")
    print("3. Valeur croissante")
    print("4. Valeur décroissante")
    print("5. Priorité croissante")
    print("6. Priorité décroissante")
    print("0. Retour")
    choix = _lire_ligne("Organisation : ")
    tris = {
        "1": ("poids croissant", lambda: session.collection.selon_poids(False)),
        "2": ("poids décroissant", lambda: session.collection.selon_poids(True)),
        "3": ("valeur croissante", lambda: session.collection.selon_valeur(False)),
        "4": ("valeur décroissante", lambda: session.collection.selon_valeur(True)),
        "5": ("priorité croissante", lambda: session.collection.selon_priorite(False)),
        "6": ("priorité décroissante", lambda: session.collection.selon_priorite(True)),
    }
    if choix == "0":
        return
    selection = tris.get(choix)
    if selection is None:
        print("Choix invalide.")
        return
    titre, produire = selection
    nombre = len(session.collection)
    print(f"Tri fusion de {nombre} colis ({titre})…")
    debut = time.perf_counter()
    tries = produire()
    print(f"Tri terminé en {(time.perf_counter() - debut) * 1_000:.2f} ms.")
    _paginer(tries, f"Colis par {titre}")


def preparer_camion(session: Session) -> None:
    """Calcule un chargement (capacité + critère)."""
    if len(session.collection) == 0:
        print("La collection est vide. Ajoutez ou chargez des colis d'abord.")
        return
    capacite = _lire_entier("Capacité maximale du camion (kg) : ", minimum=0)
    print("1. Maximiser la valeur")
    print("2. Maximiser le score valeur × priorité")
    choix = _lire_ligne("Critère : ")
    if choix not in CRITERES:
        print("Choix invalide.")
        return
    critere, libelle = CRITERES[choix]
    print("Calcul du chargement…")
    debut = time.perf_counter()
    session.chargement = preparer_chargement(
        session.collection.tous(),
        capacite,
        critere,
    )
    duree = (time.perf_counter() - debut) * 1_000
    print(f"Calcul terminé en {duree:.2f} ms. Critère : {libelle}.")
    afficher_chargement(session)


def afficher_chargement(session: Session) -> None:
    """Affiche le dernier chargement."""
    resultat = session.chargement
    if resultat is None:
        print("Aucun camion n'a encore été préparé.")
        return
    print()
    print("===== CHARGEMENT =====")
    print(f"Algorithme : {resultat.algorithme}")
    print(f"Optimal pour le critère : {'oui' if resultat.optimal else 'non'}")
    print(f"Critère : {_libelle_critere(resultat)}")
    print(f"Capacité : {resultat.capacite} kg")
    print(f"Poids chargé : {resultat.poids_total} kg")
    print(f"Capacité restante : {resultat.capacite_restante} kg")
    print(f"Valeur totale : {resultat.valeur_totale}")
    print(f"Score total (valeur × priorité) : {resultat.score_total}")
    print(f"Colis retenus : {len(resultat.colis_choisis)}")
    print(resultat.explication)
    _paginer(list(resultat.colis_choisis), "Colis chargés")


def afficher_statistiques(session: Session) -> None:
    """Affiche les stats."""
    stats = calculer(session.collection)
    print()
    print("===== STATISTIQUES =====")
    if stats["nombre"] == 0:
        print("Aucun colis.")
        return
    moyenne = stats["priorite_moyenne"]
    print(f"Nombre de colis : {stats['nombre']}")
    print(f"Poids total : {stats['poids_total']} kg")
    print(f"Valeur totale : {stats['valeur_totale']}")
    print(f"Priorité moyenne : {moyenne:.2f}")
    print(f"Poids min / max : {stats['poids_min']} / {stats['poids_max']} kg")
    print(f"Valeur min / max : {stats['valeur_min']} / {stats['valeur_max']}")
    print("Par destination :")
    for destination, effectif in sorted(stats["par_destination"].items()):
        print(f"  {destination} : {effectif}")
    print("Par priorité :")
    for priorite, effectif in sorted(stats["par_priorite"].items()):
        print(f"  {priorite} : {effectif}")


def charger_donnees(session: Session) -> None:
    """Charge l'exemple du sujet ou un jeu généré."""
    print()
    print("1. Exemple du sujet (5 colis)")
    print("2. Générer 100 colis")
    print("3. Générer 1 000 colis")
    print("4. Générer 10 000 colis")
    print("5. Générer 100 000 colis")
    print("0. Retour")
    choix = _lire_ligne("Jeu de données : ")
    jeux = {
        "1": ("exemple du sujet", list(EXEMPLE_SUJET)),
        "2": ("100 colis", None),
        "3": ("1 000 colis", None),
        "4": ("10 000 colis", None),
        "5": ("100 000 colis", None),
    }
    if choix == "0":
        return
    if choix not in jeux:
        print("Choix invalide.")
        return
    if len(session.collection) > 0 and not _confirmer(
        "Remplacer la collection actuelle ? (o/n) : "
    ):
        print("Chargement annulé.")
        return

    libelle, deja_prets = jeux[choix]
    if deja_prets is None:
        nombre = {"2": 100, "3": 1_000, "4": 10_000, "5": 100_000}[choix]
        print(f"Génération de {nombre} colis…")
        colis = generer_colis(nombre)
    else:
        colis = deja_prets
    avait_un_plan = session.chargement is not None
    session.collection = depuis_liste(colis)
    session.chargement = None
    print(f"{len(colis)} colis chargés ({libelle}).")
    if avait_un_plan:
        print("L'ancien plan de chargement a été effacé.")


def mesurer(session: Session) -> None:
    """Lance les mesures sans toucher à la collection en cours."""
    print("Mesures sur des collections temporaires.")
    print("La collection en cours n'est pas modifiée. Quelques secondes.")
    from src.benchmark import afficher, executer

    afficher(executer())


def _afficher_menu(session: Session) -> None:
    print()
    print("===== GESTION DES LIVRAISONS =====")
    print(f"Colis en mémoire : {len(session.collection)}")
    print("1. Afficher les colis")
    print("2. Ajouter un colis")
    print("3. Rechercher un colis")
    print("4. Organiser les colis")
    print("5. Préparer un camion")
    print("6. Afficher le chargement")
    print("7. Afficher les statistiques")
    print("8. Charger des données")
    print("9. Mesurer les performances")
    print("0. Quitter")


def _paginer(colis: list[Colis], titre: str) -> None:
    print()
    print(f"===== {titre.upper()} =====")
    print(f"{len(colis)} colis")
    if not colis:
        return
    debut = 0
    while debut < len(colis):
        fin = min(debut + PAGE, len(colis))
        _entete()
        for colis_courant in colis[debut:fin]:
            print(_ligne(colis_courant))
        debut = fin
        if debut < len(colis):
            if not _confirmer("Afficher la suite ? (o/n) : "):
                print(f"{len(colis) - debut} colis non affichés.")
                return


def _entete() -> None:
    print(f"{'ID':<8} {'Poids':>6} {'Valeur':>8} {'Priorité':>10}  Destination")


def _ligne(colis: Colis) -> str:
    return (
        f"{colis.identifiant:<8} {colis.poids:>6} {colis.valeur:>8} "
        f"{colis.priorite:>10}  {colis.destination}"
    )


def _libelle_critere(resultat: ResultatChargement) -> str:
    if resultat.critere == VALEUR:
        return "valeur monétaire"
    return "score = valeur × priorité (priorité haute = nombre élevé)"


def _lire_ligne(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        print()
        raise SystemExit(0)


def _lire_texte(message: str) -> str:
    while True:
        texte = _lire_ligne(message)
        if texte:
            return texte
        print("Ce champ est obligatoire.")


def _lire_entier(message: str, minimum: int | None = None) -> int:
    while True:
        saisie = _lire_ligne(message)
        try:
            valeur = int(saisie)
        except ValueError:
            print("Veuillez entrer un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"La valeur doit être supérieure ou égale à {minimum}.")
            continue
        return valeur


def _confirmer(message: str) -> bool:
    return _lire_ligne(message).lower() in {"o", "oui", "y", "yes"}
