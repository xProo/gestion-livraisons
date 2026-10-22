"""Tests du tri, de la recherche et du chargement."""

import random
import unittest

from src.chargement import (
    ALGO_DP,
    ALGO_GLOUTON,
    ALGO_RENCONTRE,
    SCORE,
    VALEUR,
    _glouton,
    _programmation_dynamique,
    _rencontre_au_milieu,
    preparer_chargement,
    score_de,
)
from src.colis import Colis, creer_colis
from src.collection import IdentifiantDejaPresent, depuis_liste
from src.donnees import EXEMPLE_SUJET, generer_colis
from src.statistiques import calculer
from src.tri import tri_fusion


def _oracle(colis, capacite, critere):
    """Force brute, seulement pour les petits lots."""
    scores = [score_de(element, critere) for element in colis]
    meilleur = 0
    nombre = len(colis)
    for masque in range(1 << nombre):
        poids = 0
        score = 0
        for indice in range(nombre):
            if masque & (1 << indice):
                poids += colis[indice].poids
                if poids > capacite:
                    break
                score += scores[indice]
        else:
            if score > meilleur:
                meilleur = score
    return meilleur


class TestColis(unittest.TestCase):
    def test_exemple_du_sujet(self):
        self.assertEqual(
            [(c.identifiant, c.poids, c.valeur, c.priorite, c.destination) for c in EXEMPLE_SUJET],
            [
                (101, 8, 20, 2, "Paris"),
                (102, 3, 10, 5, "Lille"),
                (103, 12, 40, 1, "Lyon"),
                (104, 5, 25, 4, "Paris"),
                (105, 2, 15, 3, "Lille"),
            ],
        )

    def test_refuse_les_valeurs_incoherentes(self):
        with self.assertRaises(ValueError):
            creer_colis(1, 0, 10, 1, "Paris")
        with self.assertRaises(ValueError):
            creer_colis(1, 5, -1, 1, "Paris")
        with self.assertRaises(ValueError):
            creer_colis(1, 5, 10, 0, "Paris")
        with self.assertRaises(ValueError):
            creer_colis(1, 5, 10, 1, "   ")
        with self.assertRaises(ValueError):
            Colis(True, 5, 10, 1, "Paris")

    def test_score(self):
        colis = Colis(1, 8, 20, 5, "Paris")
        self.assertEqual(colis.score(), 100)


class TestCollectionEtTri(unittest.TestCase):
    def test_ajout_recherche_et_doublon(self):
        collection = depuis_liste(list(EXEMPLE_SUJET))
        self.assertEqual(len(collection), 5)
        trouve = collection.rechercher(103)
        self.assertIsNotNone(trouve)
        self.assertEqual(trouve.destination, "Lyon")
        self.assertIsNone(collection.rechercher(999))
        with self.assertRaises(IdentifiantDejaPresent):
            collection.ajouter(Colis(101, 1, 1, 1, "Nice"))

    def test_tri_fusion_contre_le_tri_natif_et_stable(self):
        alea = random.Random(7)
        valeurs = [alea.randint(0, 20) for _ in range(200)]
        couples = list(enumerate(valeurs))
        obtenu = tri_fusion(couples, lambda couple: couple[1])
        attendu = sorted(couples, key=lambda couple: couple[1])
        self.assertEqual(obtenu, attendu)

        colis = [
            Colis(1, 5, 10, 1, "A"),
            Colis(2, 5, 30, 2, "B"),
            Colis(3, 1, 10, 4, "C"),
        ]
        par_poids = depuis_liste(colis).selon_poids()
        self.assertEqual([c.identifiant for c in par_poids], [3, 1, 2])
        par_valeur = depuis_liste(colis).selon_valeur(decroissant=True)
        self.assertEqual([c.identifiant for c in par_valeur], [2, 1, 3])

    def test_statistiques_exemple(self):
        stats = calculer(depuis_liste(list(EXEMPLE_SUJET)))
        self.assertEqual(stats["nombre"], 5)
        self.assertEqual(stats["poids_total"], 30)
        self.assertEqual(stats["valeur_totale"], 110)
        self.assertEqual(stats["par_destination"]["Paris"], 2)
        self.assertEqual(stats["par_destination"]["Lille"], 2)
        self.assertAlmostEqual(stats["priorite_moyenne"], 3.0)


class TestChargement(unittest.TestCase):
    def setUp(self):
        # A B C D, cas priorité de l'énoncé
        self.lot = [
            Colis(1, 8, 20, 5, "A"),
            Colis(2, 6, 25, 1, "B"),
            Colis(3, 5, 18, 4, "C"),
            Colis(4, 4, 14, 3, "D"),
        ]

    def test_valeur_capacite_10_et_15(self):
        court = preparer_chargement(self.lot, 10, VALEUR)
        self.assertTrue(court.optimal)
        self.assertEqual(court.algorithme, ALGO_DP)
        self.assertEqual(court.valeur_totale, 39)
        self.assertEqual({c.destination for c in court.colis_choisis}, {"B", "D"})
        self.assertLessEqual(court.poids_total, 10)

        long = preparer_chargement(self.lot, 15, VALEUR)
        self.assertEqual(long.valeur_totale, 57)
        self.assertEqual({c.destination for c in long.colis_choisis}, {"B", "C", "D"})

    def test_priorite_change_la_selection(self):
        resultat = preparer_chargement(self.lot, 10, SCORE)
        self.assertTrue(resultat.optimal)
        self.assertEqual(resultat.score_total, 114)
        self.assertEqual({c.destination for c in resultat.colis_choisis}, {"C", "D"})
        # valeur plus basse que le plan "valeur seule"
        self.assertEqual(resultat.valeur_totale, 32)

    def test_exemple_sujet_tient_entierement_dans_50_kg(self):
        resultat = preparer_chargement(list(EXEMPLE_SUJET), 50, VALEUR)
        self.assertEqual(len(resultat.colis_choisis), 5)
        self.assertEqual(resultat.valeur_totale, 110)
        self.assertEqual(resultat.poids_total, 30)

    def test_glouton_pas_toujours_optimal(self):
        # densités 6, 5, 4 -> glouton 160, optimal 220
        lot = [
            Colis(1, 10, 60, 1, "X"),
            Colis(2, 20, 100, 1, "Y"),
            Colis(3, 30, 120, 1, "Z"),
        ]
        glouton = _glouton(lot, 50, VALEUR)
        self.assertFalse(glouton.optimal)
        self.assertEqual(glouton.valeur_totale, 160)
        optimal = preparer_chargement(lot, 50, VALEUR)
        self.assertTrue(optimal.optimal)
        self.assertEqual(optimal.valeur_totale, 220)

    def test_les_trois_methodes_concordent_avec_la_force_brute(self):
        alea = random.Random(1)
        for _ in range(30):
            nombre = alea.randint(0, 12)
            lot = [
                Colis(
                    indice,
                    alea.randint(1, 15),
                    alea.randint(0, 40),
                    alea.randint(1, 5),
                    "D",
                )
                for indice in range(nombre)
            ]
            capacite = alea.randint(0, 40)
            for critere in (VALEUR, SCORE):
                attendu = _oracle(lot, capacite, critere)
                for produire in (
                    preparer_chargement,
                    lambda elements, masse, crit: _programmation_dynamique(
                        [c for c in elements if c.poids <= masse], masse, crit
                    ),
                    lambda elements, masse, crit: _rencontre_au_milieu(
                        [c for c in elements if c.poids <= masse], masse, crit
                    ),
                ):
                    if nombre == 0 or capacite == 0 or all(c.poids > capacite for c in lot):
                        resultat = preparer_chargement(lot, capacite, critere)
                    else:
                        resultat = produire(lot, capacite, critere)
                    self.assertLessEqual(resultat.poids_total, capacite)
                    self.assertEqual(score_de_total(resultat, critere), attendu)

    def test_grande_capacite_utilise_la_rencontre_au_milieu(self):
        # 20 colis, capacité énorme : DP trop grosse, n <= 36
        lot = generer_colis(20, graine=3)
        resultat = preparer_chargement(lot, 500_000, SCORE)
        self.assertEqual(resultat.algorithme, ALGO_RENCONTRE)
        self.assertTrue(resultat.optimal)
        self.assertLessEqual(resultat.poids_total, 500_000)

    def test_beaucoup_de_colis_et_grande_capacite_utilisent_le_glouton(self):
        # 80 colis et grosse capacité : glouton
        lot = generer_colis(80, graine=4)
        resultat = preparer_chargement(lot, 1_000_000, VALEUR)
        self.assertEqual(resultat.algorithme, ALGO_GLOUTON)
        self.assertFalse(resultat.optimal)
        self.assertLessEqual(resultat.poids_total, 1_000_000)

    def test_cent_colis_et_camion_de_50_kg_restent_en_programmation_dynamique(self):
        lot = generer_colis(1_000, graine=5)
        resultat = preparer_chargement(lot, 50, SCORE)
        self.assertEqual(resultat.algorithme, ALGO_DP)
        self.assertTrue(resultat.optimal)
        self.assertLessEqual(resultat.poids_total, 50)


def score_de_total(resultat, critere) -> int:
    return sum(score_de(colis, critere) for colis in resultat.colis_choisis)


if __name__ == "__main__":
    unittest.main()
