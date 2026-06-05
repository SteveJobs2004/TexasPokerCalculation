import random
import unittest

from poker_calculator import evaluate_7cards, simulate_winrate


class PokerCalculatorTest(unittest.TestCase):
    def test_evaluates_royal_flush(self):
        score, hand_name = evaluate_7cards(
            [
                (10, "H"),
                (11, "H"),
                (12, "H"),
                (13, "H"),
                (14, "H"),
                (2, "C"),
                (7, "D"),
            ]
        )

        self.assertEqual(score, (9, ()))
        self.assertEqual(hand_name, "Royal Flush")

    def test_evaluates_wheel_straight(self):
        score, hand_name = evaluate_7cards(
            [
                (14, "S"),
                (2, "H"),
                (3, "D"),
                (4, "C"),
                (5, "S"),
                (9, "H"),
                (12, "D"),
            ]
        )

        self.assertEqual(score, (4, (5,)))
        self.assertEqual(hand_name, "Straight")

    def test_uses_highest_trip_as_full_house_primary_rank(self):
        score, hand_name = evaluate_7cards(
            [
                (14, "S"),
                (14, "H"),
                (14, "D"),
                (13, "S"),
                (13, "H"),
                (13, "D"),
                (2, "C"),
            ]
        )

        self.assertEqual(score, (6, (14, 13)))
        self.assertEqual(hand_name, "Full House")

    def test_simulation_counts_every_trial(self):
        result = simulate_winrate(
            player_hand=[(14, "S"), (14, "H")],
            community_cards=[],
            num_players=2,
            num_simulations=25,
            rng=random.Random(1),
        )

        self.assertEqual(result.total, 25)
        self.assertEqual(result.wins + result.ties + result.losses, 25)

    def test_rejects_duplicate_known_cards(self):
        with self.assertRaises(ValueError):
            simulate_winrate(
                player_hand=[(14, "S"), (14, "S")],
                community_cards=[],
                num_players=2,
                num_simulations=10,
            )


if __name__ == "__main__":
    unittest.main()
